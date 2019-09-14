import socket
from email.parser import Parser

import http

IP = 'localhost'
PORT = 9091
MAX_CONNECTIONS = 1

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
server.listen(MAX_CONNECTIONS)

print('Server is running on {IP}:{PORT} ...'.format(IP=IP, PORT=PORT))

RESP = http.Response(
    status = 200,
    reason = 'OK',
    headers = {
        'Host': 'localhost',
    },
    body = bytes('Hey man', encoding='UTF-8')
)

while True:
    conn, address = server.accept()
    print("New connection from {address}".format(address=address))

    req = http.handleRequest(conn)
    http.sendResponse(conn, RESP)

    conn.close()