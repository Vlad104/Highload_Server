from email.parser import Parser
import datetime

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

MAX_LINE = 1024

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
    # raw = rfile.readline(MAX_LINE + 1)
    raw = rfile.readline()
    if len(raw) > MAX_LINE:
        raise Exception('Request line is too long')

    req_line = str(raw, 'iso-8859-1')
    req_line = req_line.rstrip('\r\n')
    words = req_line.split()            # разделяем по пробелу
    if len(words) != 3:                 # и ожидаем ровно 3 части
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
        # line = rfile.readline(MAX_LINE + 1)
        if len(line) > MAX_LINE:
            raise Exception('Header line is too long')

        if line in (b'\r\n', b'\n', b''):
            # завершаем чтение заголовков
            break

        headers.append(line)
        if len(headers) > MAX_HEADERS:
            raise Exception('Too many headers')

    sheaders = b''.join(headers).decode('iso-8859-1')
    return Parser().parsestr(sheaders)

RESP = Response(
    status = 200,
    reason = 'OK',
    headers = {
        'Host': 'localhost',
        'Date': str(datetime.datetime.now())
    },
    body = bytes('Hey man', encoding='UTF-8')
)

def sendResponse(conn, resp=RESP):
    wfile = conn.makefile('wb')
    status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
    wfile.write(status_line.encode('iso-8859-1'))

    if resp.headers:
        for key in resp.headers:
            header_line = f'{key}: {resp.headers[key]}\r\n'
            wfile.write(header_line.encode('iso-8859-1'))

    wfile.write(b'\r\n')

    if resp.body:
        wfile.write(resp.body)
        wfile.write(b'\r\n')

    wfile.flush()
    wfile.close()