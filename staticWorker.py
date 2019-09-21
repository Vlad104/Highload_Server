import os
import mimetypes

mimetypes.init()

def getStatic(root, path):

    status, newPath = getFileStatus(root, path)
    if (status != 200):
        return None, '', status

    contentType = getContentType(newPath)
    file = getFile(newPath)

    return file, contentType, status


def getFileStatus(root, path):
    try:
        if not checkPath(root, path):
            print('checkPath FAILED')
            return 404, ''

        path = f'{root}{path}'
        print(f'---- {path}')

        if not checkExisting(path):
            print('checkExisting FAILED')
            return 404, ''

        if not checkAccessToRead(path):
            print('checkAccessToRead FAILED')
            return 403, ''

        if isDir(path):
            if not isFile(f'{path}index.html'):
                print('isDir isFile FAILED')
                return 404, ''
            print('isDir isFile OK')
            return 200, f'{path}index.html'

        if not isFile(path):
            print('isFile FAILED')
            return 404, ''

        print('Request is OK')
        return 200, path

    except:
        return 405, ''


def checkPath(root, path):
    return not ('/../' in path)

def checkExisting(path):
    return os.path.exists(path)

def isDir(path):
    return os.path.isdir(path)

def isFile(path):
    return os.path.isfile(path)

def checkAccessToRead(path):
    return os.access(path, os.R_OK)

def getFile(path):
    file = os.open(path, os.O_RDONLY)
    return file

def getContentType(path):
    extention = os.path.splitext(path)[1].lower()
    return mimetypes.types_map[extention]