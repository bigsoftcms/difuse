import argparse
from filesystem import Filesystem
from fuse import FUSE
from protocol import read_message, write_message, one_time_message, listening_socket
import syscalls
from threading import Thread
import atexit
import os


class Peer():
    def __init__(self, mountpoint, bootstrap, host_port):
        os.system("mkdir -p %s" % syscalls.LOCALSTORAGE_DIR)
        sock = listening_socket(host_port)
        response = one_time_message(bootstrap, method='join', port=host_port)
        filesystem = Filesystem(bootstrap)
        thread = Thread(target=listen, args=(sock,))
        thread.daemon = True
        thread.start()
        atexit.register(shutdown, bootstrap)
        fuse = FUSE(filesystem, mountpoint, foreground=True)


def listen(sock):
    actions = {
        'chmod': syscalls.chmod,
        'create': syscalls.create,
        'getattr': syscalls.getattr,
        'open': syscalls.open,
        'read': syscalls.read,
        'readdir': syscalls.readdir,
        'unlink': syscalls.unlink,
        'write': syscalls.write,
    }

    while True:
        conn, addr = sock.accept()
        message = read_message(conn)
        method = message.pop('method')
        if method == 'write':
            message['data'] = message['data'].encode()
        try:
            ret = actions[method](**message)
            if method == 'read':
                ret = ret.decode()
            if ret is not None:
                write_message(conn, method=method, ret=ret)
            else:
                write_message(conn, method=method)
        except OSError:
            write_message(conn, method=method, errno=1)
        conn.close()


def shutdown(bootstrap):
    one_time_message(bootstrap, method='leave')
    os.system("rm -rf %s" % syscalls.LOCALSTORAGE_DIR)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mountpoint', type=str)
    parser.add_argument('boot_ip', type=str)
    parser.add_argument('boot_port', type=int)
    parser.add_argument('host_port', type=int)
    args = parser.parse_args()

    peer = Peer(args.mountpoint, (args.boot_ip, args.boot_port), args.host_port)
