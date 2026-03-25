import socket, threading, select, struct, os, sys

def send_msg(sock, data_bytes):
    header = struct.pack(">I", len(data_bytes))
    sock.sendall(header + data_bytes)

def recv_msg(sock):
    header = b""
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk: return None
        header += chunk
    length = struct.unpack(">I", header)[0]
    buf = b""
    while len(buf) < length:
        chunk = sock.recv(length - len(buf))
        if not chunk: return None
        buf += chunk
    return buf

def send_file(sock, path, chunk_size=4096):
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            sock.sendall(struct.pack(">I", len(chunk)) + chunk)
    sock.sendall(struct.pack(">I", 0))

def recv_file(sock, path):
    with open(path, "wb") as f:
        while True:
            header = b""
            while len(header) < 4:
                c = sock.recv(4 - len(header))
                if not c: return
                header += c
            length = struct.unpack(">I", header)[0]
            if length == 0: break
            buf = b""
            while len(buf) < length:
                c = sock.recv(length - len(buf))
                if not c: return
                buf += c
            f.write(buf)

SERVER_DIR = 'server_files'
os.makedirs(SERVER_DIR, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 5000))
server.listen(5)

poll_obj = select.poll()
poll_obj.register(server.fileno(), select.POLLIN)
fd_map = {server.fileno(): server}

print("POLL Server running on port 5000... (Run in Linux/WSL)")

while True:
    events = poll_obj.poll()

    for fd, event in events:
        sock = fd_map[fd]

        if sock is server:
            conn, addr = server.accept()
            poll_obj.register(conn.fileno(), select.POLLIN)
            fd_map[conn.fileno()] = conn
            print("Connected:", addr)

        elif event & select.POLLIN:
            try:
                msg = recv_msg(sock)
                if not msg:
                    poll_obj.unregister(fd)
                    del fd_map[fd]
                    sock.close()
                    continue

                if msg.startswith(b'/list'):
                    files = os.listdir(SERVER_DIR)
                    send_msg(sock, ('\n'.join(files) or 'No files').encode())

                elif msg.startswith(b'/upload'):
                    filename = msg.split(b' ', 1)[1].decode()
                    recv_file(sock, os.path.join(SERVER_DIR, filename))
                    send_msg(sock, f"Upload {filename} selesai.".encode())
                    
                    for fd_key, c in fd_map.items():
                        if c not in [server, sock]: send_msg(c, f"[Server] File baru: {filename}".encode())

                elif msg.startswith(b'/download'):
                    filename = msg.split(b' ', 1)[1].decode()
                    path = os.path.join(SERVER_DIR, filename)
                    if os.path.exists(path):
                        send_msg(sock, f'/download_ready {filename}'.encode())
                        send_file(sock, path)
                    else:
                        send_msg(sock, b'File not found')
                        
                elif msg.startswith(b'/chat'):
                    text = msg.split(b' ', 1)[1].decode()
                    for fd_key, c in fd_map.items():
                        if c not in [server, sock]: send_msg(c, f"[User {sock.getpeername()[1]}]: {text}".encode())

            except Exception:
                poll_obj.unregister(fd)
                del fd_map[fd]
                sock.close()