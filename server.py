import socket
import threading

clients = {}
addresses = {}

def handle_client(client_socket, username):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message.startswith("@"):
                recipient, msg = message[1:].split(' ', 1)
                if recipient in clients:
                    clients[recipient].send(f"Private from {username}: {msg}".encode("utf-8"))
                else:
                    client_socket.send("User not found.".encode("utf-8"))
            else:
                broadcast(f"{username}: {message}", username)
        except:
            break

    client_socket.close()
    del clients[username]
    broadcast(f"{username} has left the chat.", username)

def broadcast(message, sender_username):
    for username, client_socket in clients.items():
        if username != sender_username:
            client_socket.send(message.encode("utf-8"))

def start_server(server_socket):
    server_socket.listen()
    print("[*] Server listening on port 12345")

    while True:
        client_socket, client_address = server_socket.accept()
        client_socket.send("Enter your username: ".encode("utf-8"))
        username = client_socket.recv(1024).decode("utf-8")
        clients[username] = client_socket
        addresses[client_socket] = client_address

        print(f"[+] New connection from {client_address} as {username}")
        broadcast(f"{username} has joined the chat!", username)

        client_handler = threading.Thread(target=handle_client, args=(client_socket, username))
        client_handler.start()

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 12345))

    start_server(server_socket)
