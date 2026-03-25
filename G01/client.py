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

CLIENT_DIR = 'client_files'
os.makedirs(CLIENT_DIR, exist_ok=True)

HOST = '127.0.0.1'
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def receive():
    while True:
        try:
            msg = recv_msg(s)
            if not msg:
                print("\n[Terputus dari server]")
                break
                
            if msg.startswith(b'/download_ready'):
                filename = msg.split(b' ', 1)[1].decode()
                filepath = os.path.join(CLIENT_DIR, filename)
                print(f"\n[Mengunduh {filename} dari server...]")
                recv_file(s, filepath)
                print(f"\n[Download Selesai: {filename}]\n> ", end='')
            else:
                print("\n" + msg.decode() + "\n> ", end='')
        except Exception as e:
            break

threading.Thread(target=receive, daemon=True).start()

while True:
    print("\n=== MENU ===\n1. List files\n2. Upload file\n3. Download file\n4. Send message\n5. Exit")
    choice = input("> ")

    if choice == '1':
        send_msg(s, b'/list')

    elif choice == '2':
        filename = input("File: ")
        if not os.path.exists(filename):
            print("File not found!")
            continue
            
        send_msg(s, f'/upload {os.path.basename(filename)}'.encode())
        print(f"Uploading {filename}...")
        send_file(s, filename)

    elif choice == '3':
        filename = input("Download file: ")
        send_msg(s, f'/download {filename}'.encode())

    elif choice == '4':
        msg = input("Message: ")
        send_msg(s, f'/chat {msg}'.encode())

    elif choice == '5':
        s.close()
        break