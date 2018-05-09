import json
import socket
import sys
from construct import BytesInteger, PascalString

listen_queue_length = 10

header_len = 4
LENGTH = BytesInteger(header_len)
MESSAGE = PascalString(LENGTH, 'ascii')


def write_message(socket, **kwargs):
    message = json.dumps(kwargs)
    socket.send(MESSAGE.build(message))


def read_message(socket):
    header = socket.recv(header_len)
    length = LENGTH.parse(header)
    body = socket.recv(length)
    message = MESSAGE.parse(header + body)
    return json.loads(message)


def one_time_message(addr, **kwargs):
    """
    Parameter addr is a tuple (host, port) to be given to connect.
    """
    sock = socket.socket()
    sock.connect(addr)
    write_message(sock, **kwargs)
    message = read_message(sock)
    sock.close()
    return message


def listening_socket(port):
    sock = socket.socket()
    sock.bind(('0.0.0.0', port))
    sock.listen(listen_queue_length)
    return sock


if __name__ == '__main__':
    sock1, sock2 = socket.socketpair()
    files = {
        'lol.txt': 'lol',
        'hello.txt': 'Hello World!',
    }
    write_message(sock1, method='join', files=files)
    message = read_message(sock2)
    print(message)
