import socket, select, os

HOST, PORT = '0.0.0.0', 5002
FILES_DIR = 'server_files'

os.makedirs(FILES_DIR, exist_ok=True)

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

inputs = [server]
clients = []

print("Select server running...")

while True:
    readable, _, _ = select.select(inputs, [], [])

    for s in readable:
        if s is server:
            conn, addr = server.accept()
            inputs.append(conn)
            clients.append(conn)
            print("Connected:", addr)

        else:
            data = s.recv(1024)
            if not data:
                inputs.remove(s)
                clients.remove(s)
                s.close()
                continue

            msg = data.decode()

            if msg.startswith('/list'):
                files = os.listdir(FILES_DIR)
                s.send(('\n'.join(files) or 'No files').encode())

            else:
                for c in clients:
                    if c != s:
                        c.send(data)