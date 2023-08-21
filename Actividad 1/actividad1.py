import socket 
from utils import *

# con la siguiente línea creamos un socket orientado a conexión
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# definimos dirección donde queremos que correr el server_socket
server_address = ('localhost', 5000)

# hacemos bind del server socket a la dirección server_address
server_socket.bind(server_address)

# nos quedamos esperando, como buen server, a que llegue una petición de conexión
print('... Esperando clientes')
while True: