[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
|-------------------|------------|---------|
| Afsal Murtaza            | 5025241190        | D|
| Khairan Cherokee Musthofa               | 5025241215           | D          |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program

PROTOCOL FRAMING (Dari PPT)

Method 5 : Length Prefix : Digunakan untuk mengirim pesan/perintah (seperti teks biasa, /list, /upload). Kita akan menambahkan 4-byte header di setiap pesan yang berisi panjang ukuran pesan tersebut.

```
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
```
Method 6 : Chunked Blocks : Digunakan khusus untuk transfer file biner. File dipecah menjadi bagian-bagian (chunk) dan dikirim dengan panjangnya, lalu diakhiri dengan ukuran 0 sebagai penanda akhir (EOF).
```
def send_file(sock, path, chunk_size=4096):
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            sock.sendall(struct.pack(">I", len(chunk)) + chunk)
    sock.sendall(struct.pack(">I", 0)) # Terminator

def recv_file(sock, path):
    with open(path, "wb") as f:
        while True:
            header = b""
            while len(header) < 4:
                c = sock.recv(4 - len(header))
                if not c: return
                header += c
            length = struct.unpack(">I", header)[0]
            if length == 0: break # EOF
            buf = b""
            while len(buf) < length:
                c = sock.recv(length - len(buf))
                if not c: return
                buf += c
            f.write(buf)
```
Agar kodenya tidak panjang dan berulang, kami menggunakan fungsi PROTOCOL FRAMING tersebut di setiap file (client & server)

client.py
```
# (Masukkan PROTOCOL FRAMING)
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
                
            # Jika server mengirim file untuk di-download
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

# Spawn thread untuk receive (dari PPT)
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
```

server-sync.py
```
# (Masukkan PROTOCOL FRAMING)
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
```

server-thread.py
```

```

server-select.py
```

```

server-poll.py
```

```

## Screenshot Hasil
