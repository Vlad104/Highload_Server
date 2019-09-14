import socket
import time

IP = 'localhost'
PORT = 9091
MAX_CONNECTIONS = 1

MESSAGE = 'GET /test/test.txt HTTP/1.1\r\nHOST: example.local\r\n\r\n'

clients = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for i in range(MAX_CONNECTIONS)]
for client in clients:
    client.connect((IP, PORT))

for i in range(MAX_CONNECTIONS):
    time.sleep(0.7)
    clients[i].send(bytes(MESSAGE, encoding='UTF-8'))

for client in clients:
    data = client.recv(1024)
    print(str(data, encoding='UTF-8'))