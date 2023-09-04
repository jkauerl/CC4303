import socket 
import json
from utils import *

# con la siguiente línea creamos un socket orientado a conexión
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# definimos dirección donde queremos que correr el server_socket
server_address = ('localhost', 8000)

# hacemos bind del server socket a la dirección server_address
server_socket.bind(server_address)

# parametros para cambiar
buff_size = 1024 # En bytes


# Recibe inputs especificos
#name_json = input("Ingrese nombre del archivo json: ")
#location_json = input("Ingrese ubicación archivo json: ")
name_json = "json_actividad_http"
location_json = "Actividad 1"

name_header = ""
with open((location_json + "/" + name_json + ".json")) as file:
    # usamos json para manejar los datos
    data = json.load(file)
    name_header = data["user"] 

# luego con listen (función de sockets de python) le decimos que puede
# tener hasta 3 peticiones de conexión encoladas
# si recibiera una 4ta petición de conexión la va a rechazar
server_socket.listen(3)

# nos quedamos esperando, como buen server, a que llegue una petición de conexión
print('... Esperando clientes')
while True:

    # cuando llega una petición de conexión la aceptamos
    # y se crea un nuevo socket que se comunicará con el cliente
    new_socket, new_socket_address = server_socket.accept()

    # recibiendo el mensaje del cliente
    recv_message = new_socket.recv(buff_size)

    # parseando el mensaje y rescatando la direccion de destino
    parsed_message = parse_HTTP_message(recv_message)

    is_forbidden = check_blocked_sites(parsed_message[0]["first_line"], location_json, name_json)
    if is_forbidden:
        new_socket.send(forbidden_message.encode())
        
        new_socket.close()
        break

    parsed_message[0].update({"X-ElQuePregunta: ": name_header})
    parsed_message = [parsed_message[0], parsed_message[1]]

    proxy_client_address = (parsed_message[0]["Host"], 80)
 
    # conectandose al servidor desde el proxy
    proxy_client_socket.connect(proxy_client_address)

    proxy_message = create_HTTP_message(parsed_message)

    # Se manda el mensaje al servidor
    proxy_client_socket.send(proxy_message)

    # Finalmente esperamos una respuesta del servidor
    # Para ello debemos definir el tamaño del buffer de recepción
    buffer_size = 10000000
    message_server = proxy_client_socket.recv(buffer_size)

    # modificar el mensaje para remplazar contenido inadecuado
    recieved_message_server = parse_HTTP_message(message_server)

    modified_message_server = replace_forbidden_words(recieved_message_server, location_json, name_json)

    send_message_client = create_HTTP_message(modified_message_server)

    new_socket.send(send_message_client)

    # cerramos la conexión con el servidor
    proxy_client_socket.close()

    # cerramos la conexión
    new_socket.close()

