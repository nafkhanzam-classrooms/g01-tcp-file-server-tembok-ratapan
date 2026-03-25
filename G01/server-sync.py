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
server.listen(1)

print("SYNC Server (Blocking) running on port 5000...")

while True:
    conn, addr = server.accept()
    print("Connected:", addr)

    while True:
        try:
            msg = recv_msg(conn)
            if not msg: break

            if msg.startswith(b'/list'):
                files = os.listdir(SERVER_DIR)
                send_msg(conn, ('\n'.join(files) or 'No files').encode())

            elif msg.startswith(b'/upload'):
                filename = msg.split(b' ', 1)[1].decode()
                recv_file(conn, os.path.join(SERVER_DIR, filename))
                send_msg(conn, f"Upload {filename} selesai.".encode())

            elif msg.startswith(b'/download'):
                filename = msg.split(b' ', 1)[1].decode()
                path = os.path.join(SERVER_DIR, filename)
                if os.path.exists(path):
                    send_msg(conn, f'/download_ready {filename}'.encode())
                    send_file(conn, path)
                else:
                    send_msg(conn, b'File not found')
                    
            elif msg.startswith(b'/chat'):
                text = msg.split(b' ', 1)[1].decode()
                send_msg(conn, f"[Server SYNC tidak bisa broadcast. Pesanmu: {text}]".encode())

        except Exception:
            break

    print("Disconnected:", addr)
    conn.close()