import socket
import select
import time
import random
import os

import myHttp

IP = 'localhost'
PORT = 9091
MAX_CONNECTIONS = 1

def createSocket():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind((IP, PORT))
    server.listen(MAX_CONNECTIONS)

    return server

def main():
    print('Starting server on {}:{} ...'.format(IP, PORT))
    server = createSocket()
    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN | select.EPOLLET)

    try:
        connections = {}
        requests = {}
        responses = {}
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if fileno == server.fileno():
                    try:
                        while True:
                            conn, address = server.accept()
                            conn.setblocking(0)
                            epoll.register(conn.fileno(), select.EPOLLIN | select.EPOLLET)
                            connections[conn.fileno()] = conn
                            requests[conn.fileno()] = b''
                    except socket.error:
                        pass

                elif event & select.EPOLLIN:
                    requests[fileno] = myHttp.handleRequest(connections[fileno])
                    epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                    responses[fileno] = myHttp.makeResponse(requests[fileno])


                elif event & select.EPOLLOUT:
                    myHttp.sendResponse(connections[fileno], responses[fileno])
                    responses[fileno] = None

                    if responses[fileno] is None:
                        epoll.modify(fileno, select.EPOLLET)
                        connections[fileno].shutdown(socket.SHUT_RDWR)

                elif event & select.EPOLLHUP:
                    epoll.unregister(fileno)
                    connections[fileno].close()
                    del connections[fileno]

    except KeyboardInterrupt:
        print ('KeyboardInterrupt =(')

    finally:
        print ("Server stoped")
        epoll.unregister(server.fileno())
        epoll.close()
        server.close()

main()