import socket
import threading

clients = []
key_map = {}  # cheie -> client_socket

def broadcast(message):
    for c in clients:
        try:
            c.sendall((message + '\n').encode())
        except:
            continue

def handle_client(client_socket):
    clients.append(client_socket)
    client_socket.sendall(f"CHEI_INITIAL|{','.join(key_map.keys())}\n".encode())

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            parts = message.split('|')
            command = parts[0]
            key = parts[1] if len(parts) > 1 else None

            if command == 'PUBLISH':
                if key not in key_map:
                    key_map[key] = client_socket
                    broadcast(f"NEW_KEY|{key}")
                else:
                    client_socket.sendall(f"ERROR|Cheia '{key}' exista deja\n".encode())

            elif command == 'REQUEST':
                requester_index = clients.index(client_socket)
                owner = key_map.get(key)
                if owner:
                    owner.sendall(f"REQUEST_OBJECT|{key}|{requester_index}\n".encode())
                else:
                    client_socket.sendall(f"ERROR|Cheia '{key}' nu exista\n".encode())

            elif command == 'TRANSFER':
                to_index = int(parts[2])
                object_data = '|'.join(parts[3:])
                destination = clients[to_index]
                destination.sendall(f"OBJECT_RECEIVED|{key}|{object_data}\n".encode())

            elif command == 'DELETE':
                if key_map.get(key) == client_socket:
                    del key_map[key]
                    broadcast(f"DELETE_KEY|{key}")
                else:
                    client_socket.sendall(f"ERROR|Nu poti sterge cheia '{key}'\n".encode())

    finally:
        client_socket.close()
        for k, v in list(key_map.items()):
            if v == client_socket:
                del key_map[k]
                broadcast(f"DELETE_KEY|{k}")
        clients.remove(client_socket)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 5000))
    server.listen(5)
    print("Server pornit pe portul 5000")

    while True:
        client_socket, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

if _name_ == "_main_":
    start_server()
