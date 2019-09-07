import socket

IP = 'localhost'
PORT = 9091
MAX_CONNECTIONS = 2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
server.listen(MAX_CONNECTIONS)

print('Server is running on {IP}:{PORT} ...'.format(IP=IP, PORT=PORT))

while True:
    conn, address = server.accept()
    print("New connection from {address}".format(address=address))

    data = conn.recv(1024)
    print(str(data))

    conn.send(bytes('Hello from server!', encoding='UTF-8'))

    conn.close()