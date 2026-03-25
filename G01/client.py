import socket, threading, sys, os

HOST = '127.0.0.1'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5001

s = socket.socket()
s.connect((HOST, PORT))

def receive():
    while True:
        try:
            data = s.recv(1024)
            if not data:
                break
            if data.endswith(b'EOF'):
                print("\n[File received]\n")
            else:
                print("\n[Server]:", data.decode(), "\n> ", end='')
        except:
            break

threading.Thread(target=receive, daemon=True).start()

while True:
    print("""
=== MENU ===
1. List files
2. Upload file
3. Download file
4. Send message
5. Exit
""")

    choice = input("> ")

    if choice == '1':
        s.send(b'/list')

    elif choice == '2':
        filename = input("File: ")
        if not os.path.exists(filename):
            print("File not found!")
            continue

        s.send(f'/upload {os.path.basename(filename)}'.encode())
        with open(filename, 'rb') as f:
            while chunk := f.read(1024):
                s.send(chunk)
        s.send(b'EOF')

    elif choice == '3':
        filename = input("Download file: ")
        s.send(f'/download {filename}'.encode())

    elif choice == '4':
        msg = input("Message: ")
        s.send(msg.encode())

    elif choice == '5':
        s.close()
        break