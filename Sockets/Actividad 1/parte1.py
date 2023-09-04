import socket 
import json
from utils import *

# con la siguiente línea creamos un socket orientado a conexión
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# definimos dirección donde queremos que correr el server_socket
server_address = ('localhost', 9000)

# hacemos bind del server socket a la dirección server_address
server_socket.bind(server_address)

# parametros para cambiar
buff_size = 1024 # En bytes


#name_json = input("Ingrese nombre del archivo json: ")
#location_json = input("Ingrese ubicación archivo json: ")
name_json = "json_actividad_http"
location_json = "Actividad 1"
with open((location_json + "/" + name_json) + ".json") as file:
    # usamos json para manejar los datos
    data = json.load(file)
    name_header = data["user"] 

response_head += name_header + "\r\n\r\n"

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

    http = create_HTTP_message(mensaje)

    http_response = response_head + response_body

    new_socket.send(http_response.encode())

    # cerramos la conexión
    # notar que la dirección que se imprime indica un número de puerto distinto al 8000
    new_socket.close()
