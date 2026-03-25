import socket, select, os

HOST, PORT = '0.0.0.0', 5003
FILES_DIR = 'server_files'

os.makedirs(FILES_DIR, exist_ok=True)

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

poller = select.poll()
poller.register(server, select.POLLIN)

fds = {server.fileno(): server}

print("Poll server running...")

while True:
    events = poller.poll()

    for fd, flag in events:
        s = fds[fd]

        if s is server:
            conn, addr = server.accept()
            poller.register(conn, select.POLLIN)
            fds[conn.fileno()] = conn
            print("Connected:", addr)

        else:
            data = s.recv(1024)

            if not data:
                poller.unregister(fd)
                del fds[fd]
                s.close()

            else:
                for c in fds.values():
                    if c not in (server, s):
                        c.send(data)