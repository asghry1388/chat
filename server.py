import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

def receive_messages(conn):
    buffer = b""
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                print("\nConnection closed.")
                break
            buffer += data
            while b"\n" in buffer:
                raw, buffer = buffer.split(b"\n", 1)
                if raw:
                    print("\nOther:", raw.decode("utf-8", errors="replace"))
                    print("You: ", end="", flush=True)
        except (ConnectionResetError, BrokenPipeError, OSError):
            print("\nConnection lost.")
            break

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)
print(f"Waiting for connection on port {PORT}...")
conn, address = server.accept()
print("Connected:", address)
threading.Thread(target=receive_messages, args=(conn,), daemon=True).start()

while True:
    try:
        message = input("You: ")
        if message.lower() == "/exit":
            break
        conn.sendall((message + "\n").encode("utf-8"))
    except (ConnectionResetError, BrokenPipeError, OSError):
        print("Connection lost.")
        break

conn.close()
server.close()
