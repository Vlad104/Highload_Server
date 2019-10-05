from email.parser import Parser
import datetime
import os
import re
import urllib.parse

import staticWorker

class Request:
    def __init__(self, method, target, version, headers, rfile):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.rfile = rfile

class Response:
    def __init__(self, status, reason, headers=None, body=None):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body

STATUSES = {
    200: 'OK',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Not Allowed'
}

SERVER_NAME = 'python_select_epoll'
RECV_SIZE = 64*1024
OS_READ_SIZE = 1024*1024

def handleRequest(conn):
    # return parseRequest(conn)
    return parseRequestViaFile(conn)

# not used
def parseRequest(conn):
    try:
        buff = b''
        while True:
            temp = b''
            temp = conn.recv(RECV_SIZE)
            if not temp:
                break
            buff += temp

        strBuff = str(buff, 'UTF-8')
        lines = strBuff.rstrip('\r\n')

        method, target, ver = parseFirstLine(lines[0])
        headers = parseHeaders(lines[1:])
        return Request(method, target, ver, headers, rfile)
    except:
        return None

def parseFirstLine(line):
    params = line.split()
    method, target, ver = params

    return method, target, ver

def parseHeaders(lines):
    headers = []
    for line in lines:
        if line in (b'\r\n', b'\n', b''):
            break
        headers.append(line)

    sheaders = b''.join(headers).decode('UTF-8')
    return Parser().parsestr(sheaders)

def makeResponse(root, req):
    method = req.method

    if method == 'GET':
        return responseToGet(root, req)
    elif method == 'HEAD':
        return responseToHead(root, req)
    else:
        return responseToError(req)

def responseToHead(root, req):
    resp = responseCommon(root, req)
    resp.body = None

    return resp

def responseToGet(root, req):
    return responseCommon(root, req)

def responseCommon(root, req):
    body, contentType, status = makeBody(root, req)
    connectionType = 'keep-alive'

    headers = {}
    if status == 200:
        headers = {
            'Server': SERVER_NAME,
            'Date': str(datetime.datetime.now()),
            'Connection': connectionType,
            'Content-Length': len(body),
            'Content-Type': contentType
        }
    else:
        headers = {
            'Server': SERVER_NAME,
            'Date': str(datetime.datetime.now()),
            'Connection': connectionType
        }

    return Response(status, STATUSES[status], headers, body)


def responseToError(req):
    return Response(405, STATUSES[405])

def makeBody(root, req):
    file, contentType, status = getFile(root, req)
    if (status != 200):
        return '', '', status

    fileContent = b''
    while True:
        buff = os.read(file, OS_READ_SIZE)
        if not buff:
            break
        fileContent += buff
    os.close(file)

    return fileContent, contentType, 200

def getFile(root, req):
    path = req.target.split('?')[0]
    path = urllib.parse.unquote(path)

    return staticWorker.getStatic(root, path)

# not used
def sendResponse(conn, resp):
    data = bytes(f'HTTP/1.1 {resp.status} {resp.reason}\r\n', 'UTF-8')

    if resp.headers:
        for key in resp.headers:
            data += bytes(f'{key}: {resp.headers[key]}\r\n', 'UTF-8')

    data += b'\r\n'

    if resp.body:
        data += resp.body
        data += b'\r\n'

    while len(data) > 0:
        bytesSent = conn.send(data)
        data = data[bytesSent:]


def parseRequestViaFile(conn):
    try:
        rfile = conn.makefile('rb')
        method, target, ver = parseFirstLineViaFile(rfile)
        headers = parseHeadersViaFile(rfile)
        return Request(method, target, ver, headers, rfile)
    except:
        return None

def parseFirstLineViaFile(rfile):
    raw = rfile.readline()
    line = str(raw, 'UTF-8')
    line = line.rstrip('\r\n')
    params = line.split()
    method, target, ver = params

    return method, target, ver

def parseHeadersViaFile(rfile):
    headers = []
    while True:
        line = rfile.readline()
        if line in (b'\r\n', b'\n', b''):
            break
        headers.append(line)

    sheaders = b''.join(headers).decode('UTF-8')
    return Parser().parsestr(sheaders)

def sendResponseViaFile(conn, resp):
    wfile = conn.makefile('wb')
    status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
    wfile.write(status_line.encode('UTF-8'))

    if resp.headers:
        for key in resp.headers:
            header_line = f'{key}: {resp.headers[key]}\r\n'
            wfile.write(header_line.encode('UTF-8'))

    wfile.write(b'\r\n')

    if resp.body:
        wfile.write(resp.body)
        wfile.write(b'\r\n')

    wfile.flush()
    wfile.close()