from email.parser import Parser
import datetime
import os

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
    403: 'Forbiten',
    404: 'Not found',
    405: '405'
}

SERVER_NAME = 'python_select_epoll'

def handleRequest(conn):
    return parseRequest(conn)

def parseRequest(conn):
    rfile = conn.makefile('rb')
    method, target, ver = parseLine(rfile)
    headers = parseHeaders(rfile)

    host = headers.get('Host')
    if not host:
      raise Exception('Bad request')

    return Request(method, target, ver, headers, rfile)

def parseLine(rfile):
    raw = rfile.readline()

    req_line = str(raw, 'iso-8859-1')
    req_line = req_line.rstrip('\r\n')
    words = req_line.split()
    if len(words) != 3:
        raise Exception('Malformed request line')

    method, target, ver = words
    if ver != 'HTTP/1.1':
        raise Exception('Unexpected HTTP version')

    return method, target, ver

MAX_HEADERS = 100
def parseHeaders(rfile):
    headers = []
    while True:
        line = rfile.readline()

        if line in (b'\r\n', b'\n', b''):
            break

        headers.append(line)
        if len(headers) > MAX_HEADERS:
            raise Exception('Too many headers')

    sheaders = b''.join(headers).decode('iso-8859-1')
    return Parser().parsestr(sheaders)

def makeResponse(root, req):
    method = req.method

    if method == 'GET':
        resp = responseToGet(root, req)
    elif method == 'HEAD':
        resp = responseToHead(root, req)
    else:
        resp = responseToError(req)

    return resp

def responseToHead(root, req):
    _, _, status = findFile(root, req)

    headers = {
        'Server': SERVER_NAME,
        'Date': str(datetime.datetime.now()),
        'Connection': 'keep-alive'
    }

    return Response(status, STATUSES[status], headers)

def responseToGet(root, req):
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
    file, contentType, status = findFile(root, req)
    if (status != 200):
        return '', status

    fileContent = b''
    while True:
        buff = os.read(file, 1024)
        if not buff:
            break
        fileContent += buff
    os.close(file)

    return fileContent, contentType, 200

def findFile(root, req):
    path = req.target
    if path == '' or path == '/':
        path = '/index.html'

    path = f'{root}{path}'

    if not os.path.isfile(path):
        return '', '', 404
    
    if not checkRoot(path):
        return '', '', 403

    file = os.open(path, os.O_RDONLY)
    extention = os.path.splitext(path)[1][1:].strip().lower()
    contentType = f'text/{extention};charset=utf8'

    return file, contentType, 200

def checkRoot(path):
    # extention = os.path.splitext(path)[1][1:].strip().lower()
    # return extention == 'html'
    return True


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