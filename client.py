import socket
import threading
import json

from shared_object import SharedObject

owned_keys = set()
key_values = {}

def receive_messages(sock):
    while True:
        data = sock.recv(1024).decode().strip()
        if not data:
            break
        parts = data.split('|')
        command = parts[0]

        if command == 'CHEI_INITIAL':
            print('Chei existente:', parts[1])

        elif command == 'NEW_KEY':
            print(f"\n[NOTIFICARE] Cheie noua: {parts[1]}")

        elif command == 'DELETE_KEY':
            print(f"\n[NOTIFICARE] Cheie stearsa: {parts[1]}")

        elif command == 'REQUEST_OBJECT':
            key = parts[1]
            requester_index = parts[2]
            valoare = key_values.get(key, f"Continut necunoscut pentru {key}")
            obj = SharedObject(valoare)
            message = f"TRANSFER|{key}|{requester_index}|{json.dumps(obj._dict_)}"
            sock.sendall((message + '\n').encode())

        elif command == 'OBJECT_RECEIVED':
            key = parts[1]
            data = parts[2]
            print(f"[OBIECT PRIMIT] {key}: {data}")

        elif command == 'ERROR':
            print(f"[EROARE] {parts[1]}")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 5000))
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        cmd = input("\nComanda (PUBLISH, REQUEST, DELETE): ").strip().upper()
        if cmd == 'PUBLISH':
            key = input("Cheie: ").strip()
            value = input("Valoare obiect: ").strip()
            obj = SharedObject(value)
            message = f"PUBLISH|{key}|{json.dumps(obj._dict_)}"
            sock.sendall((message + '\n').encode())
            owned_keys.add(key)
            key_values[key] = value
        elif cmd == 'REQUEST':
            key = input("Cheia de cautat: ").strip()
            sock.sendall(f"REQUEST|{key}\n".encode())
        elif cmd == 'DELETE':
            key = input("Cheie de sters: ").strip()
            if key in owned_keys:
                sock.sendall(f"DELETE|{key}\n".encode())
                owned_keys.remove(key)
                key_values.pop(key, None)
            else:
                print("Nu esti proprietarul acestei chei!")
        else:
            print("Comanda necunoscuta.")

if _name_ == "_main_":
    main()
