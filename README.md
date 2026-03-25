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
## Screenshot Hasil
