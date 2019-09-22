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

def handleRequest(conn):
    return parseRequest(conn)

def parseRequest(conn):
    try:
        rfile = conn.makefile('rb')
        method, target, ver = parseFirstLine(rfile)
        headers = parseHeaders(rfile)
        return Request(method, target, ver, headers, rfile)
    except:
        return None

def parseFirstLine(rfile):
    raw = rfile.readline()
    line = str(raw, 'UTF-8')
    line = line.rstrip('\r\n')
    params = line.split()
    method, target, ver = params

    return method, target, ver

def parseHeaders(rfile):
    headers = []
    while True:
        line = rfile.readline()
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
    resp = responseGetOrHead(root, req)
    resp.body = None

    return resp

def responseToGet(root, req):
    return responseGetOrHead(root, req)

def responseGetOrHead(root, req):
    body, contentType, status = makeBody(root, req)

    headers = {}
    if status == 200:
        headers = {
            'Server': SERVER_NAME,
            'Date': str(datetime.datetime.now()),
            'Connection': 'keep-alive',
            'Content-Length': len(body),
            'Content-Type': contentType
        }
    else:
        headers = {
            'Server': SERVER_NAME,
            'Date': str(datetime.datetime.now()),
            'Connection': 'keep-alive'
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
        buff = os.read(file, 1024)
        if not buff:
            break
        fileContent += buff
    os.close(file)

    return fileContent, contentType, 200

def getFile(root, req):
    path = req.target.split('?')[0]
    path = urllib.parse.unquote(path)

    return staticWorker.getStatic(root, path)

def sendResponse(conn, resp):
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