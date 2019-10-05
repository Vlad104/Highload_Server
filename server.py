import socket
import select
import multiprocessing as mp

import myHttp
import myConfigurator

def createSocket(ip, port, max_connections):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, port))
    server.listen(max_connections)

    return server

def log(req, res):
    print(f'Response for {req.method} {req.target}')
    print(f'Status: {res.status}')
    print(f'Header: {res.headers}')
    print(f'\n')


def cpusFork():
    ip, port, cpu_limit, root, max_connections = myConfigurator.config()
    server = createSocket(ip, port, max_connections)
    print(f'Starting server on {ip}:{port} ...')
    print(f'Static dir:{root}')
    procs = list()
    for _ in range(cpu_limit):
        d = dict(server=server, root=root)
        p = mp.Process(target=main, kwargs=d)
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
        print('joined')

def main(server, root):
    # myMulticore.fork(cpu_limit)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN | select.EPOLLET)

    connections = {}
    requests = {}
    responses = {}

    try:
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                try:
                    if fileno == server.fileno():
                        try:
                            while True:
                                conn, _ = server.accept()
                                conn.setblocking(False)
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
                        else:
                            pass

                    elif event & select.EPOLLOUT:
                        myHttp.sendResponseViaFile(connections[fileno], responses[fileno])
                        del requests[fileno]
                        del responses[fileno]
                        epoll.modify(fileno, select.EPOLLET)
                        try:
                            connections[fileno].shutdown(socket.SHUT_RDWR)
                        except:
                            pass

                    elif event & select.EPOLLHUP:
                        epoll.unregister(fileno)
                        connections[fileno].close()
                        del connections[fileno]
                except:
                    pass

    except KeyboardInterrupt:
        print ('KeyboardInterrupt')

    finally:
        print ("Server stopped")
        epoll.unregister(server.fileno())
        epoll.close()
        server.close()

cpusFork()