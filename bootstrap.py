#!/usr/bin/env python3

from protocol import write_message, read_message, listening_socket
import argparse
from errno import ENOENT, EEXIST
from threading import Thread
import sys


class Bootstrap():
    def __init__(self, port):
        self.addrs = []
        self.files = {}  # map: file -> addr = (ip, port)
        sock = listening_socket(port)

        actions = {
            'join': self.join,
            'leave': self.leave,
            'readdir': self.readdir,
            'find': self.find,
            'create': self.create,
            'unlink': self.unlink
        }

        thread = Thread(target=debug, args=(self,))
        thread.daemon = True
        thread.start()

        try:
            while True:
                connsock, addr = sock.accept()
                message = read_message(connsock)
                actions[message.pop('method')](connsock, addr, message)
                connsock.close()
        except KeyboardInterrupt:
            pass # return from constructor

    def join(self, connsock, addr, message):
        self.addrs.append((addr[0], message['port']))
        write_message(connsock, method='join')  # For consistent hashing, need to send files

    def leave(self, connsock, addr, message):
        port = [t[1] for t in self.addrs if t[0] == addr[0]][0]
        self.addrs.remove((addr[0], port))
        self.files = {k: v for k, v in self.files.items() if v != (addr[0], port)}
        # For consistent hashing, need to get files
        write_message(connsock, method='leave')

    def find(self, connsock, addr, message):
        try:
            addr = self.files[message['path']]
            write_message(connsock, method='find', addr=addr)
        except KeyError:
            write_message(connsock, method='find', errno=ENOENT)

    def readdir(self, connsock, addr, message):
        write_message(connsock, method='readdir', ret=[file[1:] for file in self.files.keys()])

    def create(self, connsock, addr, message):
        if message['path'] in self.files:
            write_message(connsock, method='create', errno=EEXIST)
        else:
            port = [t[1] for t in self.addrs if t[0] == addr[0]][0]
            self.files[message['path']] = (addr[0], port)
            write_message(connsock, method='create')

    def unlink(self, connsock, addr, message):
        self.files.pop(message['path'])
        write_message(connsock, method='unlink')


def debug(bootstrap):
    for line in sys.stdin:
        if line.rstrip('\n') == 'addrs':
            print(bootstrap.addrs)
        elif line.rstrip('\n') == 'files':
            print(bootstrap.files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('boot_port', type=int)
    args = parser.parse_args()
    b = Bootstrap(args.boot_port)
