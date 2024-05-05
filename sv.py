import threading
import socket
import ssl

host = '127.0.0.1'  
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Tạo một context SSL/TLS cho máy chủ
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile="certificate.pem", keyfile="key.pem")

def broadcast(message):
    for client in clients:
        client.send(message)

clients = []
nicknames = []

def receive():
    while True:
        client_socket, address = server.accept()
        print(f"Connected with {str(address)}")
        
        # Bọc socket trong kết nối SSL/TLS
        ssl_client_socket = ssl_context.wrap_socket(client_socket, server_side=True)
        
        ssl_client_socket.send('NICK'.encode('utf-8'))
        nickname = ssl_client_socket.recv(1024)
        
        nicknames.append(nickname)
        clients.append(ssl_client_socket)

        print(f'Nickname of client is {nickname}!')
        broadcast(f'{nickname} joined the chat'.encode('utf-8'))
        ssl_client_socket.send('Connected to server'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(ssl_client_socket,))
        thread.start()

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]} says {message}")
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat'.encode('utf-8'))
            nicknames.remove(nickname)
            break


print("Server is listening on port ", port)
receive()
