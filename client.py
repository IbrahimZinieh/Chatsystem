import socket
import threading
import os

def receive_messages(client_socket):
    """
    Receives messages from the server and prints them.

    Args:
        client_socket (socket.socket): The socket representing the client connection.
    """
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message.startswith("FILE"):
                _, sender, filename, filesize = message.split()
                filesize = int(filesize)
                receive_file(client_socket, filename, filesize)
                print(f"Received file '{filename}' from {sender}")
            else:
                print(message)
        except:
            break

def receive_file(client_socket, filename, filesize):
    """
    Receives file data from the server and saves it.

    Args:
        client_socket (socket.socket): The socket representing the client connection.
        filename (str): The name of the file to be saved.
        filesize (int): The size of the file to receive.
    """
    bytes_received = 0
    with open(filename, 'wb') as f:
        while bytes_received < filesize:
            data = client_socket.recv(min(filesize - bytes_received, 1024))
            f.write(data)
            bytes_received += len(data)

def send_file(client_socket, recipient, filename):
    """
    Sends a file to the specified recipient.

    Args:
        client_socket (socket.socket): The socket representing the client connection.
        recipient (str): The username of the recipient.
        filename (str): The name of the file to send.
    """
    if os.path.exists(filename):
        filesize = os.path.getsize(filename)
        client_socket.send(f"FILE {recipient} {filename} {filesize}".encode("utf-8"))
        with open(filename, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                client_socket.send(data)
    else:
        print("File not found.")

def start_client(client_socket):
    """
    Starts the client, connects to the server, and handles user input.
    """
    client_socket.connect(("127.0.0.1", 12345))
    username = input(client_socket.recv(1024).decode("utf-8"))
    client_socket.send(username.encode("utf-8"))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        message = input()
        if message.startswith("FILE"):
            _, recipient, filename = message.split()
            send_file(client_socket, recipient, filename)
        else:
            client_socket.send(message.encode("utf-8"))

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    start_client(client_socket)
