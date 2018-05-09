import syscalls
from fuse import Operations, FuseOSError
from protocol import one_time_message
import os

class Filesystem(Operations):
    def __init__(self, bootstrap):
        self.bootstrap = bootstrap

    def create(self, path, mode):
        resp = one_time_message(self.bootstrap, method='create', path=path)
        if 'errno' in resp:
            return 0
        syscalls.create(path, mode)
        return 0

    def getattr(self, path, fh=None):
        if syscalls.exists(path):
            return syscalls.getattr(path)
        resp = one_time_message(self.bootstrap, method='find', path=path)
        if 'errno' in resp:
            raise FuseOSError(resp['errno'])
        resp = one_time_message(tuple(resp['addr']), method='getattr', path=path)
        return resp['ret']

    def open(self, path, flags):
        if syscalls.exists(path):
            try:
                return syscalls.open(path, flags)
            except OSError as e:
                raise FuseOSError(e.errno)
        resp = one_time_message(self.bootstrap, method='find', path=path)
        if 'errno' in resp:
            raise FuseOSError(resp['errno'])
        resp = one_time_message(tuple(resp['addr']), method='open', path=path, flags=flags)
        return resp['ret']

    def read(self, path, size, offset, fh):
        if syscalls.exists(path):
            return syscalls.read(path, size, offset)
        resp = one_time_message(self.bootstrap, method='find', path=path)
        if 'errno' in resp:
            raise FuseOSError(resp['errno'])
        resp = one_time_message(tuple(resp['addr']), method='read', path=path, size=size, offset=offset)
        return resp['ret'].encode()

    def readdir(self, path, fh):
        resp = one_time_message(self.bootstrap, method='readdir')
        return resp['ret']

    def unlink(self, path):
        if syscalls.exists(path):
            resp = one_time_message(self.bootstrap, method='unlink', path=path)
            if 'errno' in resp:
                raise FuseOSError(resp['errno'])
            syscalls.unlink(path)
            return
        resp = one_time_message(self.bootstrap, method='find', path=path)
        if 'errno' in resp:
            raise FuseOSError(resp['errno'])
        one_time_message(tuple(resp['addr']), method='unlink', path=path)
        one_time_message(self.bootstrap, method='unlink', path=path)

    def write(self, path, data, offset, fh):
        if syscalls.exists(path):
            return syscalls.write(path, data, offset)
        resp = one_time_message(self.bootstrap, method='find', path=path)
        if 'errno' in resp:
            raise FuseOSError(resp['errno'])
        resp = one_time_message(tuple(resp['addr']), method='write', path=path, data=data.decode(), offset=offset)
        return resp['ret']
