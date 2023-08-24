import socket 
from utils import *

# con la siguiente línea creamos un socket orientado a conexión
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# definimos dirección donde queremos que correr el server_socket
server_address = ('localhost', 8000)

# hacemos bind del server socket a la dirección server_address
server_socket.bind(server_address)

# parametros para cambiar
buff_size = 1024 # En bytes
# definimos el path donde se encuentra el archivo que queremos enviar
path = f"Actividad 1/actividad1.html"
file = open(path, "r")
response_body = file.read()
response_head = """HTTP/1.1 200 OK
Server: nginx/1.17.0
Date: Thu, 24 Aug 2023 15:54:05 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 145
Connection: keep-alive
Access-Control-Allow-Origin: *
X-ElQuePregunta: Javier Kauer

"""

# luego con listen (función de sockets de python) le decimos que puede
# tener hasta 3 peticiones de conexión encoladas
# si recibiera una 4ta petición de conexión la va a rechazar
server_socket.listen(1)

# nos quedamos esperando, como buen server, a que llegue una petición de conexión
print('... Esperando clientes')
while True:

    # cuando llega una petición de conexión la aceptamos
    # y se crea un nuevo socket que se comunicará con el cliente
    new_socket, new_socket_address = server_socket.accept()

    recv_message = new_socket.recv(buff_size)

    mensaje = parse_HTTP_message(recv_message)
    # parse_HTTP_message(recv_message)

    # print(mensaje)
    print("a")
    http = create_HTTP_message(mensaje)
    print(http)

    print("test")
    print(response_head + response_body)

    http_response = response_head + response_body

    new_socket.send(http_response.encode())

    # cerramos la conexión
    # notar que la dirección que se imprime indica un número de puerto distinto al 8000
    new_socket.close()
