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
            return 404, ''

        path = f'{root}{path}'

        if not checkExisting(path):
            return 404, ''

        if not checkAccessToRead(path):
            return 403, ''

        if isDir(path):
            if not isFile(f'{path}index.html'):
                # return 404, ''
                return 403, ''
            return 200, f'{path}index.html'

        if not isFile(path):
            return 404, ''

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