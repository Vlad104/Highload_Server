import socket
import select
import time
import random
import os
import configparser

import myHttp

CONFIG_PATH = '/etc/httpd.conf'
MAX_CONNECTIONS = 1000

def config(mode='DEV'):
    config = configparser.ConfigParser()
    if (os.path.isfile(CONFIG_PATH)):
        config.read(CONFIG_PATH)
        ip = config[mode]['ip']
        port = config[mode]['port']
        cpu_limit = config[mode]['cpu_limit']
        root = config[mode]['document_root']

        return ip, int(port), int(cpu_limit), root
    else:
        config[mode] = {
            'ip': '0.0.0.0',
            'port': '80',
            'cpu_limit': '4',
            'thread_limit': '256',
            'document_root': '/var/www/html',
        }

        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)

        return '0.0.0.0', 80, 4, '/var/www/html'

def doFork(cpu_limit = 1):
    pids = []
    for _ in range(1, cpu_limit):
        pid = os.fork()
        if pid == 0:
            break
        pids.append(pid)

    return pids

def createSocket(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind((ip, port))
    server.listen(MAX_CONNECTIONS)

    return server

def log(req, res):
    print(f'Response for {req.method} {req.target}')
    print(f'Status: {res.status}')
    print(f'Header: {res.headers}')
    print(f'\n')

def main():
    ip, port, cpu_limit, root = config()
    print(f'Starting server on {ip}:{port} ...')
    print(f'Static dir:{root}')
    print(f'Server using {cpu_limit} cpus')
    server = createSocket(ip, port)

    pids = doFork(cpu_limit)
    print('pids: ', pids)

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
                            conn, _ = server.accept()
                            conn.setblocking(0)
                            epoll.register(conn.fileno(), select.EPOLLIN | select.EPOLLET)
                            connections[conn.fileno()] = conn
                            requests[conn.fileno()] = b''
                    except socket.error:
                        pass

                elif event & select.EPOLLIN:
                    req = myHttp.handleRequest(connections[fileno])
                    if req:
                        requests[fileno] = req
                        epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                        responses[fileno] = myHttp.makeResponse(root, requests[fileno])


                elif event & select.EPOLLOUT:
                    myHttp.sendResponse(connections[fileno], responses[fileno])
                    log(requests[fileno], responses[fileno])
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
        print ("Server stopped")
        epoll.unregister(server.fileno())
        epoll.close()
        server.close()

main()