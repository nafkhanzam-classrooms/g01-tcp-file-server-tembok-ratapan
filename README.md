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
https://youtu.be/zECTXYZrQpA
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

### client.py
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

### server-sync.py
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

-socket.socket(AF_INET, SOCK_STREAM)

 membuat socket

`AF_INET` → pakai IPv4
`SOCK_STREAM` → TCP (connection-oriented)

- setsockopt(SO_REUSEADDR, 1)

 menghindari error:

Address already in use

artinya:

port bisa dipakai ulang tanpa nunggu timeout OS

- bind(('0.0.0.0', 5000))

menentukan alamat server

`0.0.0.0` → menerima dari semua IP

`5000` → port yang dibuka

- listen(1)

server mulai “mendengar” koneksi

angka 1 = backlog:

jumlah antrian koneksi yang ditahan OS

artinya:

kalau banyak client datang → hanya 1 yang diantrikan

- while True

 server berjalan terus (infinite loop)

- conn, addr = server.accept()

Fungsi:

menunggu client masuk

saat ada client → return:

`conn` = socket khusus untuk client itu

`addr` = alamat client

### server-thread.py
```
# (Masukkan PROTOCOL FRAMING)
SERVER_DIR = 'server_files'
os.makedirs(SERVER_DIR, exist_ok=True)
clients = []

def handle_client(conn, addr):
    clients.append(conn)
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
                
                # Broadcast bahwa ada file baru
                for c in clients:
                    if c != conn: send_msg(c, f"[Server] User {addr[1]} mengunggah {filename}".encode())

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
                for c in clients:
                    if c != conn: send_msg(c, f"[User {addr[1]}]: {text}".encode())

        except Exception:
            break

    conn.close()
    if conn in clients: clients.remove(conn)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 5000))
server.listen(5)
print("THREAD Server running on port 5000...")

while True:
    conn, addr = server.accept()
    # Spawn Thread seperti di PPT
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
```

- clients = []
 list global untuk menyimpan semua koneksi client

Fungsi:

untuk broadcast (chat)

untuk tracking siapa saja yang terhubung

- def handle_client(conn, addr):
  
   fungsi yang dijalankan oleh thread

    conn = socket client
  
    addr = alamat client (IP, port)
  
- clients.append(conn)
  
 menambahkan client ke daftar aktif

supaya bisa kirim pesan ke client lain

- print("Connected:", addr)
  
 hanya logging (biar tahu siapa yang connect)

- while True:
 loop utama untuk melayani client ini

selama client masih terhubung

server terus menunggu request

- msg = recv_msg(conn)
  
  menerima data dari client

    ini blocking call
  
    thread ini “menunggu” input client

- if not msg: break

    kondisi client disconnect

client close connection

error jaringan

maka:

keluar dari loop

thread selesai

### server-select.py
```
# (Masukkan PROTOCOL FRAMING)
SERVER_DIR = 'server_files'
os.makedirs(SERVER_DIR, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 5000))
server.listen(5)

input_sockets = [server] # Seperti dari PPT
print("SELECT Server running on port 5000...")

while True:
    read_ready, _, _ = select.select(input_sockets, [], []) # dari PPT 

    for sock in read_ready:
        if sock == server:
            conn, addr = server.accept()
            input_sockets.append(conn)
            print("Connected:", addr)
        else:
            try:
                msg = recv_msg(sock)
                if not msg:
                    input_sockets.remove(sock)
                    sock.close()
                    continue

                if msg.startswith(b'/list'):
                    files = os.listdir(SERVER_DIR)
                    send_msg(sock, ('\n'.join(files) or 'No files').encode())

                elif msg.startswith(b'/upload'):
                    filename = msg.split(b' ', 1)[1].decode()
                    recv_file(sock, os.path.join(SERVER_DIR, filename))
                    send_msg(sock, f"Upload {filename} selesai.".encode())
                    
                    for c in input_sockets:
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
                    for c in input_sockets:
                        if c not in [server, sock]:
                            send_msg(c, f"[User {sock.getpeername()[1]}]: {text}".encode())

            except Exception:
                input_sockets.remove(sock)
                sock.close()
```

- input_sockets = [server]

 ini adalah daftar semua socket yang dipantau

-   Inisialisasi Server

```
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5000))
server.listen(5)
```

sama seperti sync:

buat server TCP
buka port 5000

- input_sockets = [server]

list ini berisi:

awalnya hanya server

nanti:

akan berisi semua client juga

memonitor banyak socket sekaligus

- select.select(...)
```
read_ready, _, _ = select.select(input_sockets, [], [])
```

 fungsi ini:

memantau semua socket di input_sockets

return socket yang siap dibaca

- Loop Utama
  
for sock in read_ready:

 hanya memproses socket yang siap

- Jika Server Socket

if sock == server:

artinya:

ada client baru masuk

- Accept Client
  
conn, addr = server.accept()

input_sockets.append(conn)

penting:

client ditambahkan ke list

supaya ikut dimonitor

- Jika Client Socket
  
else:
    msg = recv_msg(sock)

artinya:

client ini mengirim data

- Jika Client Disconnect
  
if not msg:
    input_sockets.remove(sock)
    sock.close()

hapus dari monitoring

### server-poll.py
```
# (Masukkan PROTOCOL FRAMING)
SERVER_DIR = 'server_files'
os.makedirs(SERVER_DIR, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 5000))
server.listen(5)

# Setup POLL seperti dari PPT
poll_obj = select.poll()
poll_obj.register(server.fileno(), select.POLLIN)
fd_map = {server.fileno(): server}

print("POLL Server running on port 5000... (Run in Linux/WSL)")

while True:
    events = poll_obj.poll() # dari PPT

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
```

- Inisialisasi Poll

```
poll_obj = select.poll()
poll_obj.register(server.fileno(), select.POLLIN)
```

 Membuat poll object

 Mendaftarkan server untuk dipantau (event: ada data masuk)

- Mapping FD ke Socket
```fd_map = {server.fileno(): server}```

 Karena poll pakai file descriptor (angka)

 Kita simpan mapping ke socket asli

- Ambil Event (INTI)

events = poll_obj.poll()

 Mengambil semua socket yang siap
 Mirip select, tapi lebih scalable

- Loop Event

for fd, event in events:
```
    sock = fd_map[fd]
```

Ambil socket dari fd

- Jika Server (Client Baru)
```
if sock is server:
    conn, addr = server.accept()
    poll_obj.register(conn.fileno(), select.POLLIN)
    fd_map[conn.fileno()] = conn
```

Ada client baru:

diterima

didaftarkan ke poll

dimasukkan ke map

- Jika Client Kirim Data
```
elif event & select.POLLIN:
```

Artinya:

socket siap dibaca

- Terima Data
```
msg = recv_msg(sock)
```
Ambil pesan dari client

- Jika Client Disconnect
```
if not msg:
    poll_obj.unregister(fd)
    del fd_map[fd]
    sock.close()
```

Hapus dari:

poll

map

tutup koneksi

## Screenshot Hasil

### Server-Sync

<img width="1213" height="212" alt="image" src="https://github.com/user-attachments/assets/8f0ddd12-e36c-4d8c-8c33-080e6a371bf2" />
(Run Server-Sync)


<img width="1219" height="276" alt="image" src="https://github.com/user-attachments/assets/8dccdb5c-ae56-4652-a71a-33f3bd24d2fb" />
(Add Client 1)


<img width="1212" height="257" alt="image" src="https://github.com/user-attachments/assets/a1a15e3c-d4ba-4c68-a928-a698be065e6e" />
(Add Client 2)


<img width="1211" height="493" alt="image" src="https://github.com/user-attachments/assets/3268c795-4ff9-4550-b242-b6f10204b0ea" />
(Client 1 Block)


### Server-Select

<img width="1210" height="267" alt="image" src="https://github.com/user-attachments/assets/bcc777eb-5578-49e0-aa2f-8635e0a21361" />
(Run Server-Select)


<img width="1209" height="507" alt="image" src="https://github.com/user-attachments/assets/728a9b0b-54b8-4689-a38d-6d1419455e1a" />
(Add 3 Client)


<img width="1210" height="511" alt="image" src="https://github.com/user-attachments/assets/9f0e50dd-bb16-4baa-810d-c61e42d863c7" />
(Upload dari Client 2)


<img width="281" height="244" alt="image" src="https://github.com/user-attachments/assets/e5b3fd15-e1dc-4e06-a9a4-cd44eb77d030" />
(Hasil Upload masuk di Server File)


<img width="1214" height="581" alt="image" src="https://github.com/user-attachments/assets/fd31303d-2c53-43c2-a51a-8158bd027cb5" />
(Download dari Client 3)


<img width="274" height="271" alt="image" src="https://github.com/user-attachments/assets/01f2659c-06a8-4a7c-ba6c-6a6ca8793cb7" />
(Hasil Download masuk di Client File)


<img width="1210" height="640" alt="image" src="https://github.com/user-attachments/assets/728955b4-eff9-4fce-be45-047821558cce" />
(Kirim Chat dari Client 2)


<img width="1211" height="641" alt="image" src="https://github.com/user-attachments/assets/059ced85-ece9-43e3-9096-e04dc539e012" />
(Kirim Chat dari Client 3)
