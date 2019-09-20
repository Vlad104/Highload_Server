import socket
import select
import time
import random
import os
import configparser

import myHttp

CONFIG_PATH = './httpd.conf'
IP = 'localhost'
PORT = 9091
MAX_CONNECTIONS = 1
CPU_LIMIT = 1
ROOT = './'

def config(mode='DEV'):
    config = configparser.ConfigParser()
    if (os.path.isfile(CONFIG_PATH)):
        config.read(CONFIG_PATH)
        IP = config[mode]['ip']
        PORT = config[mode]['port']
        CPU_LIMIT = config[mode]['cpu_limit']
        ROOT = config[mode]['document_root']
    else:
        config[mode] = {
            'ip': 'localhost',
            'port': '9091',
            'cpu_limit': '4',
            'thread_limit': '256',
            'document_root': '/var/www/html',
        }

        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)

def doFork():
    pids = []
    for i in range(CPU_LIMIT):
        pid = os.fork()
        pids.append(pid)

    return pids

def createSocket():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind((IP, PORT))
    server.listen(MAX_CONNECTIONS)

    return server

def main():
    config()
    print(f'Starting server on {IP}:{PORT} ...')
    pids = doFork()
    print(f'Server using {len(pids)} cpus\n Pids: {pids} ...')
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
        print ('KeyboardInterrupt')

    finally:
        print ("Server stoped")
        epoll.unregister(server.fileno())
        epoll.close()
        server.close()

main()