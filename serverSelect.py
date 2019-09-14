import socket
import select
import time
import random

import http

IP = 'localhost'
PORT = 9091
MAX_CONNECTIONS = 1

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
            req = http.handleRequest(resource)
            doWork(req)
            if resource not in WriteList:
                WriteList.append(resource)
            else:
                clearResource(resource)

def handlerForWrite(writeList):
    for resource in writeList:
        try:
            body = readFile()
            http.sendResponse(resource, body)
        except OSError:
            clearResource(resource)

def clearResource(resource):
    if resource in WriteList:
        WriteList.remove(resource)
    if resource in ReadList:
        ReadList.remove(resource)
    resource.close()
    print('closing connection...')
    
def doWork(req):
    print(req)

def readFile():
    path = 'http.py'
    f = open(path, 'rb')
    return f.read()

def main():
    server = createSocket()
    ReadList.append(server)
    print('Server is running on {IP}:{PORT} ...'.format(IP=IP, PORT=PORT))

    try:
        while ReadList:
            readList, writeList, _ = select.select(ReadList, WriteList, [])
            handlerForRead(readList, server)
            handlerForWrite(writeList)
    except KeyboardInterrupt:
        print('Server was stopped')

main()