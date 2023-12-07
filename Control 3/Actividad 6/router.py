import sys
import socket
from utils import *

# Diccionario con mensajes fragmentados
dict_of_fragments = {}

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

    if int(parsed_message["ttl"]) == 0:
        print(f"Se recibió {decoded_message} con TTL 0")
        continue

    # Caso en que el paquete es para el router
    if parsed_message["port"] == router_puerto:
        
        id = int(parsed_message["id"])
        
        # Caso en donde el no hay un elemento con ese id en el diccionario
        if id not in dict_of_fragments:
            dict_of_fragments[id] = [parsed_message]
        # Caso en donde el elemento ya existe en el diccionario
        else:
            for fragments in dict_of_fragments[id]:
                if fragments == parsed_message:
                    break
                else:
                    dict_of_fragments[id].append(parsed_message)
                    break

        parsed_fragmented_list = dict_of_fragments[id]

        fragmented_list = [create_packet(fragment).encode() for fragment in parsed_fragmented_list]

        # Tratar de rearmar el paquete
        reassembled_IP_packet = reassemble_IP_packet(fragmented_list)

        # Caso en donde no se puede rearmar el paquete
        if reassembled_IP_packet == None:
            continue

        message = parse_packet(reassembled_IP_packet.encode())["message"]
        
        print(message)
        continue
    else:
        (next_hop_ip, next_hop_port), next_hop_mtu = check_routers(router_table_name, (parsed_message["ip"], parsed_message["port"]))        

        # Manejar el caso en donde no se puede hacer forwarding
        if next_hop_ip == None:
            print(f"no hay rutas hacia {parsed_message['port']} para paquete {decoded_message}")
            continue

        # Fragmentar el paquete si es necesario
        fragmented_packets = fragment_IP_packet(coded_message, int(next_hop_mtu))

        # Enviar cada paquete fragmentado
        for fragment in fragmented_packets:

            parsed_fragment = parse_packet(fragment)

            # Decrementar el TTL
            parsed_fragment["ttl"] = (str(int(parsed_fragment["ttl"]) - 1)).zfill(3)

            # Crear el nuevo paquete IP
            new_packet = create_packet(parsed_fragment).encode()

            # Forwarding
            udp_socket.sendto(new_packet, (next_hop_ip, int(next_hop_port)))
        
        # Imprimir en pantalla que se está haciendo forwarindg
        print(f"redirigiendo paquete {decoded_message} con destino final {parsed_message['port']} desde {router_puerto} hacia {next_hop_port}")
        continue

# Cerrar conexión
udp_socket.close()