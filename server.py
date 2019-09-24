import socket
import select

import myHttp
import myMulticore
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

def main():
    ip, port, cpu_limit, root, max_connections = myConfigurator.config()
    print(f'Starting server on {ip}:{port} ...')
    print(f'Static dir:{root}')
    server = createSocket(ip, port, max_connections)

    myMulticore.fork(cpu_limit)

    epoll = select.epoll()
    epoll.register(server.fileno(), select.EPOLLIN | select.EPOLLET)

    connections = {}
    requests = {}
    responses = {}

    try:
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if fileno == server.fileno():
                    try:
                        while True:
                            conn, _ = server.accept()
                            conn.setblocking(False)
                            epoll.register(conn.fileno(), select.EPOLLIN | select.EPOLLET)
                            connections[conn.fileno()] = conn
                            requests[conn.fileno()] = b''
                    except socket.error:
                        # print(socket.error)
                        pass

                elif event & select.EPOLLIN:
                    req = myHttp.handleRequest(connections[fileno])
                    if req:
                        requests[fileno] = req
                        epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                        responses[fileno] = myHttp.makeResponse(root, requests[fileno])
                    else:
                        pass
                        # print('405')

                elif event & select.EPOLLOUT:
                    myHttp.sendResponse(connections[fileno], responses[fileno])
                    # log(requests[fileno], responses[fileno])
                    # del requests[fileno]
                    # del responses[fileno]
                    epoll.modify(fileno, select.EPOLLET)
                    try:
                        connections[fileno].shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                        # print('Force shout down')

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

if __name__ == '__main__':
    main()