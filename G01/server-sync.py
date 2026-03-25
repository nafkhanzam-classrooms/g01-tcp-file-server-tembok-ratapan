import socket, os

HOST = 'localhost'
PORT = 5000
FILES_DIR = 'server_files'

os.makedirs(FILES_DIR, exist_ok=True)

s = socket.socket()
s.bind((HOST, PORT))
s.listen(1)

print("Sync server running...")

while True:
    conn, addr = s.accept()
    print("Connected:", addr)

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            if data.startswith('/list'):
                files = os.listdir(FILES_DIR)
                conn.send(('\n'.join(files) or 'No files').encode())

            elif data.startswith('/upload'):
                _, filename = data.split()
                with open(os.path.join(FILES_DIR, filename), 'wb') as f:
                    while True:
                        chunk = conn.recv(1024)
                        if chunk.endswith(b'EOF'):
                            f.write(chunk[:-3])
                            break
                        f.write(chunk)
                conn.send(b'Upload done')

            elif data.startswith('/download'):
                _, filename = data.split()
                path = os.path.join(FILES_DIR, filename)
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        while chunk := f.read(1024):
                            conn.send(chunk)
                    conn.send(b'EOF')
                else:
                    conn.send(b'File not found')

        except:
            break

    conn.close()