import sys
import socket
from utils import *


# Rescatar los valores al invocar el script
headers = sys.argv[1]
initial_ip = sys.argv[2]
initial_port = int(sys.argv[3])

file_path = "archivo_prueba.txt"

lines = []

# Abrir archivo y leerlo linea por linea
with open(file_path, "r") as f:
    for line in f:
        # Crear el paquete IP
        IP_packet = headers + line
        lines.append(IP_packet)


# Creación del socket no orientado a conexion
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bloquear el socket y hacer que escuche en el puerto correctamente
udp_socket.setblocking(True)
udp_socket.bind((initial_ip, initial_port))

# Enviar los paquetes IP
for line in lines:
    udp_socket.sendto(line.encode(), (initial_ip, initial_port))
