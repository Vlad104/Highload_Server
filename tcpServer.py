import socket
import select
import time
import random

IP = 'localhost'
PORT = 9091
MAX_CONNECTIONS = 12

ReadList = list()
WriteList = list()

def createSocket():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind((IP, PORT))
    server.listen(MAX_CONNECTIONS)

    return server

def handlerForRead(readList, server):
    for resource in readList:
        if resource is server:
            conn, address = resource.accept()
            conn.setblocking(0)
            ReadList.append(conn)
            print("new connection from {address}".format(address=address))
        else:
            data = ''
            try:
                data = resource.recv(1024)
            except ConnectionResetError:
                pass

            if data:
                doWork(data)
                if resource not in WriteList:
                    WriteList.append(resource)

            else:
                clearResource(resource)

def handlerForWrite(writeList):
    for resource in writeList:
        try:
            resource.send(bytes('Hello from server!', encoding='UTF-8'))
        except OSError:
            clearResource(resource)

def clearResource(resource):
    if resource in WriteList:
        WriteList.remove(resource)
    if resource in ReadList:
        ReadList.remove(resource)
    resource.close()
    print('closing connection...')
    
def doWork(data):
    print("getting data: {data}".format(data=str(data)))
    sec = random.randint(0, 5)
    time.sleep(sec)

def main():
    server = createSocket()
    ReadList.append(server)
    print('Server is running on {IP}:{PORT} ...'.format(IP=IP, PORT=PORT))

    try:
        while ReadList:
            readList, writeList, exceptional = select.select(ReadList, WriteList, ReadList)
            handlerForRead(readList, server)
            handlerForWrite(writeList)
    except KeyboardInterrupt:
        print('Server was stopped')

main()