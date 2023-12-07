import sys
import socket
from utils import *

# Rescatar los valores al invocar el script
router_ip = sys.argv[1]
router_puerto = int(sys.argv[2])
router_table_name = sys.argv[3]

# Creación del socket no orientado a conexion
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bloquear el socket y hacer que escuche en el puerto correctamente
udp_socket.bind((router_ip, router_puerto))
udp_socket.setblocking(True)

while True:

    # Recibir el paquete IP
    message, address = udp_socket.recvfrom(1024)
    decoded_message = message.decode().rstrip("\n")
    coded_message = decoded_message.encode()

    parsed_message = parse_packet(coded_message)

    if parsed_message["ttl"] == 0:
        print(f"Se recibió {decoded_message} con TTL 0")
        continue

    if parsed_message["port"] == router_puerto:
        print(parsed_message["message"].rstrip("\n"))
        continue
    else:
        next_hop_ip, next_hop_port = check_routers(router_table_name, (parsed_message["ip"], parsed_message["port"]))
        
        # Manejar el caso en donde no se hace forwarding
        if next_hop_ip == None:
            print(f"no hay rutas hacia {parsed_message['port']} para paquete {decoded_message}")
            continue

        # Decrementar el TTL

        parsed_message["ttl"] -= 1

        # Crear el nuevo paquete IP
        new_packet = create_packet(parsed_message).encode()

        # Forwarding
        udp_socket.sendto(new_packet, (next_hop_ip, int(next_hop_port)))
        
        # Imprimir en pantalla que se está haciendo forwarindg
        print(f"redirigiendo paquete {decoded_message} con destino final {parsed_message['port']} desde {router_puerto} hacia {next_hop_port}")
        continue

# Cerrar conexión
udp_socket.close()