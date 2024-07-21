import socket
import threading

clients = {}
addresses = {}

def handle_client(client_socket, username):
    """
    Handles incoming messages from a client.

    Args:
        client_socket (socket.socket): The socket representing the client connection.
        username (str): The username of the client.
    """
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message.startswith("@"):
                recipient, msg = message[1:].split(' ', 1)
                if recipient in clients:
                    clients[recipient].send(f"Private from {username}: {msg}".encode("utf-8"))
                else:
                    client_socket.send("User not found.".encode("utf-8"))
            elif message.startswith("FILE"):
                _, recipient, filename, filesize = message.split()
                filesize = int(filesize)
                if recipient in clients:
                    clients[recipient].send(f"FILE {username} {filename} {filesize}".encode("utf-8"))
                    transfer_file(client_socket, clients[recipient], filesize)
                else:
                    client_socket.send("User not found.".encode("utf-8"))
            else:
                broadcast(f"{username}: {message}", username)
        except:
            break

    client_socket.close()
    del clients[username]
    broadcast(f"{username} has left the chat.", username)

def transfer_file(sender_socket, receiver_socket, filesize):
    """
    Transfers file data from the sender to the receiver.

    Args:
        sender_socket (socket.socket): The socket representing the sender.
        receiver_socket (socket.socket): The socket representing the receiver.
        filesize (int): The size of the file to transfer.
    """
    bytes_received = 0
    while bytes_received < filesize:
        data = sender_socket.recv(min(filesize - bytes_received, 1024))
        receiver_socket.send(data)
        bytes_received += len(data)

def broadcast(message, sender_username):
    """
    Sends a message to all clients except the sender.

    Args:
        message (str): The message to be broadcasted.
        sender_username (str): The username of the sender.
    """
    for username, client_socket in clients.items():
        if username != sender_username:
            client_socket.send(message.encode("utf-8"))

def start_server(server_socket):
    """
    Starts the server to listen for incoming connections.

    Args:
        server_socket (socket.socket): The socket representing the server.
    """
    server_socket.listen()
    print("[*] Server listening on port 12345")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_socket.send("Enter your username: ".encode("utf-8"))
            if len(clients.keys()) == 0:
                print("[*] First user connected.")
                client_socket.send("No other users online.".encode("utf-8"))
            else:
                client_socket.send(f"Users online: {', '.join(clients.keys())}".encode("utf-8"))
            username = client_socket.recv(1024).decode("utf-8")
            clients[username] = client_socket
            addresses[client_socket] = client_address

            print(f"[+] New connection from {client_address} as {username}")
            broadcast(f"{username} has joined the chat!", username)

            client_handler = threading.Thread(target=handle_client, args=(client_socket, username))
            client_handler.start()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 12345))

    start_server(server_socket)
