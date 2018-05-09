import stat
import os


LOCALSTORAGE_DIR = '.localstorage'

def localpath(path):
    # return os.path.join(LOCALSTORAGE_DIR, os.path.basename(path))
    return LOCALSTORAGE_DIR + path

def exists(path):
    return os.path.exists(localpath(path))

def chmod(path, mode):
    os.chmod(localpath(path), mode)
    return 0

def create(path, mode):
    os.close(os.open(localpath(path), os.O_CREAT, mode=mode))
    return 0

def getattr(path, fh=None):
    stat_dict = os.stat(localpath(path))
    return dict(
        st_mode=stat_dict.st_mode,
        st_ino=stat_dict.st_ino,
        st_dev=stat_dict.st_dev,
        st_nlink=stat_dict.st_nlink,
        st_uid=stat_dict.st_uid,
        st_gid=stat_dict.st_gid,
        st_size=stat_dict.st_size,
        st_atime=stat_dict.st_atime,
        st_mtime=stat_dict.st_mtime,
        st_ctime=stat_dict.st_ctime,
    )

def open(path, flags):
    os.close(os.open(localpath(path), flags))
    return 0

def read(path, size, offset, fh=None):
    fd = os.open(localpath(path), os.O_RDONLY)
    os.lseek(fd, offset, os.SEEK_SET)
    data = os.read(fd, size)
    os.close(fd)
    return data

def readdir(path, fh=None):
    dirs = ['.', '..']
    dirs.extend(os.listdir(path=localpath(path)))
    return dirs

def unlink(path):
    os.remove(localpath(path))
    return 0

def write(path, data, offset, fh=None):
    fd = os.open(localpath(path), os.O_RDWR)
    os.lseek(fd, offset, os.SEEK_SET)
    numbytes = os.write(fd, data)
    os.close(fd)
    return numbytes

if __name__ == '__main__':
    print(exists('/'))
#    unlink('lul.txt')
    print(readdir('/', None))