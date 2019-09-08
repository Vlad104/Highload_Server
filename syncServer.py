import socket
from email.parser import Parser

IP = 'localhost'
PORT = 9091
MAX_CONNECTIONS = 1

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
server.listen(MAX_CONNECTIONS)

print('Server is running on {IP}:{PORT} ...'.format(IP=IP, PORT=PORT))

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

def parseRequest(conn):
    rfile = conn.makefile('rb')
    method, target, ver = parseLine(rfile)
    headers = parseHeaders(rfile)

    host = headers.get('Host')
    if not host:
      raise Exception('Bad request')

    return Request(method, target, ver, headers, rfile)

def parseLine(rfile):
    raw = rfile.readline(MAX_LINE + 1)
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
        line = rfile.readline(MAX_LINE + 1)
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
    },
    body = bytes('Hey man', encoding='UTF-8')
)

def sendResponse(conn, resp):
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

    wfile.flush()
    wfile.close()

while True:
    conn, address = server.accept()
    print("New connection from {address}".format(address=address))

    req = parseRequest(conn)
    # print(req)
    # handleRequest(req)
    sendResponse(conn, RESP)

    conn.close()