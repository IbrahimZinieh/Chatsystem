import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)
        except:
            break

def start_client(client_socket):
    client_socket.connect(("127.0.0.1", 12345))
    username = input(client_socket.recv(1024).decode("utf-8"))
    client_socket.send(username.encode("utf-8"))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        message = input()
        client_socket.send(message.encode("utf-8"))

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    start_client(client_socket)
