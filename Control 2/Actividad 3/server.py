import socket

# creamos el socket servidor (no orientado a conexión)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# definimos dirección donde queremos que correr el server_socket
server_address = ('localhost', 5000)

# hacemos bind del server socket a la dirección server_address
server_socket.bind(server_address)

messages = ""
while True:
    message, client_address = server_socket.recvfrom(16 + 12)
    messages += message.decode()
    print(message)
    if message == None:
        break

print(messages)