from math import ceil
import socket

# Funciones de utilidad

round_robin = []
# two = 0

def parse_packet(IP_packet):
    decoded_IP_packet = IP_packet.decode()

    # Obtener los valores de la IP, puerto y mensaje
    ip, port, ttl, id, offset, size, flag, message = decoded_IP_packet.split(",")

    # Guardar los valores en un diccionario
    parsed_packet = { "ip": ip, "port": int(port), "ttl": ttl.zfill(3), 
                        "id": id.zfill(8), "offset": offset.zfill(8), "size": size.zfill(8), 
                        "flag": int(flag), "message": message}
    return parsed_packet

def create_packet(parsed_packet):

    # Rescatar los valores del diccionario
    ip = parsed_packet["ip"]
    port = parsed_packet["port"]
    ttl = parsed_packet["ttl"]
    id = parsed_packet["id"]
    offset = parsed_packet["offset"]
    size = parsed_packet["size"]
    flag = parsed_packet["flag"]
    message = parsed_packet["message"]

    # Crear el paquete IP y retornarlo
    IP_packet = f"{ip},{port},{ttl},{id},{offset},{size},{flag},{message}"
    return IP_packet

def check_routers(routes_file_name, destination_address):
    # Crear el path del archivo de rutas
    path = "tablas_de_rutas/" + routes_file_name

    # Abrir el archivo de rutas
    with open(path, "r") as f:
        global round_robin
        line_number = len(f.readlines())

        if line_number > 0 and round_robin == []:
            round_robin = [0]*line_number

        line_counter = 0
        possible_next_hop_router = []
        possible_next_hop_index = []


        f.seek(0)
        # Ir chequeando linea por linea las rutas disponibles
        for line in f:
            _, start_port, end_port, next_hop_ip, next_hop_port, mtu = line.split(" ")

            # Si la dirección de destino está en el rango de puertos de la ruta, se agrega a la lista de posibles puertos
            if destination_address[1] >= int(start_port) and destination_address[1] <= int(end_port):
                possible_next_hop_router.append(((next_hop_ip, int(next_hop_port)), mtu))
                possible_next_hop_index.append(line_counter)

            line_counter += 1

        # Si hay posibles puertos, se escoge el que tenga menos paquetes enviados
        if possible_next_hop_router != []:
            
            # Inicializar los valores de la primera ruta como el mínimo
            next_hop_ip = None
            next_hop_port = None
            next_hop_tmu = None

            min_round_robin = 10000
            min_round_robin_index = 0

            # Recorrer los valores de las rutas posibles y escoger la que tenga menos paquetes enviados
            for i in range(len(possible_next_hop_router)):
                if round_robin[possible_next_hop_index[i]] < min_round_robin:
                    min_round_robin = round_robin[possible_next_hop_index[i]]
                    min_round_robin_index = possible_next_hop_index[i]
                    next_hop_ip = possible_next_hop_router[i][0][0]
                    next_hop_port = possible_next_hop_router[i][0][1]
                    next_hop_tmu = possible_next_hop_router[i][1]

            # Actualizar el valor de paquetes enviados
            round_robin[min_round_robin_index] += 1
            return ((next_hop_ip, next_hop_port), next_hop_tmu)
        else:
            return ((None, None), None)
        
def fragment_IP_packet(IP_packet, mtu):

    # Obtener el largo del paquete IP
    IP_packet_size = len(IP_packet)

    # Chequear si el paquete IP cabe en el MTU
    if IP_packet_size <= mtu:
        return [IP_packet]
    
    # Si no cabe el paquete IP en el MTU, se fragmenta 
    parsed_IP_packet = parse_packet(IP_packet)
    fragmented_message_size = mtu - 48
    number_of_fragments = ceil(int(parsed_IP_packet["size"]) / fragmented_message_size)

    fragmented_IP_packets = []

    for i in range(number_of_fragments):

        # Obtener el offset
        offset = str(int(parsed_IP_packet["offset"]) + i * fragmented_message_size).zfill(8)

        # Obtener el tamaño del fragmento
        if i == number_of_fragments - 1:
            fragment_size = str(int(parsed_IP_packet["size"]) - (i * fragmented_message_size)).zfill(8)
        else:
            fragment_size = str(fragmented_message_size).zfill(8)

        # Obtener el flag
        if i == number_of_fragments - 1:
            flag = 0
        else:
            flag = 1

        # Obtener el mensaje
        message = parsed_IP_packet["message"][i * fragmented_message_size : (i + 1) * fragmented_message_size]

        # Crear el paquete IP
        parsed_packet = { "ip": parsed_IP_packet["ip"], "port": parsed_IP_packet["port"], "ttl": parsed_IP_packet["ttl"], 
                        "id": parsed_IP_packet["id"], "offset": offset, "size": fragment_size, 
                        "flag": flag, "message": message}

        # Crear el paquete IP
        parsed_packet = create_packet(parsed_packet).encode()

        # Agregar el paquete IP a la lista de fragmentos
        fragmented_IP_packets.append(parsed_packet)

    return fragmented_IP_packets

def reassemble_IP_packet(fragment_list):
    
    # Revisar si la lista de fragmentos está vacía entonces retorna None
    if fragment_list == []:
        return None
    
    # Parsear la lista de fragmentos
    parsed_fragment_list = [parse_packet(fragment) for fragment in fragment_list]


    # Revisar si la lista de fragmentos tiene un solo elemento
    if len(parsed_fragment_list) == 1:
        if parsed_fragment_list[0]["flag"] == 0:
            return parsed_fragment_list[0]["message"]
        else:
            return None
        
    # Ordenar la lista de fragmentos por offset
    parsed_fragment_list.sort(key=lambda x: int(x["offset"]))

    # Revisa si el offset del primer fragmento es 0
    if parsed_fragment_list[0]["offset"] != "00000000":
        return None

    # Revisar si el flag del último fragmento es 0
    if parsed_fragment_list[-1]["flag"] != 0:
        return None

    message = ""
    added_offset = 0

    # Iterar por la lista de fragmentos para rearmar el mensaje
    for fragment in parsed_fragment_list:
        # Si el offset es igual al offset agregado, se agrega el mensaje
        if int(fragment["offset"]) == added_offset:
            message += fragment["message"]
            added_offset += int(fragment["size"])
        # Si no, se retorna None
        else:
            return None
        
    # Crear el paquete IP
    parsed_packet = { "ip": parsed_fragment_list[0]["ip"], "port": parsed_fragment_list[0]["port"], "ttl": parsed_fragment_list[0]["ttl"], 
                        "id": parsed_fragment_list[0]["id"], "offset": parsed_fragment_list[0]["offset"], "size": (str(len(message.encode()))).zfill(8), 
                        "flag": 0, "message": message}
    
    IP_packet = create_packet(parsed_packet)

    return IP_packet

def create_BGP_message(router_port, ttl, id, routes, destiny_address):

    possible_next_hop_router = []

    for i in routes:
        possible_next_hop_router.append(i)

    possible_next_hop_router = [[int(port) for port in route] for route in possible_next_hop_router]

    # Crear el el mensaje BGP
    BGP_message = f"BGP_ROUTES\n{router_port}\n"

    BGP_message = BGP_message + "\n".join([f"{' '.join(map(str, route))}" for route in possible_next_hop_router]) + "\nEND_BGP_ROUTES"

    # Crear el paquete IP
    IP_packet = f"""{destiny_address[0]},{destiny_address[1]},{ttl},{(str(id)).zfill(3)},{(str(0)).zfill(8)},{(str(len(BGP_message.encode())).zfill(8))},{0},{BGP_message}"""    
        
    return IP_packet

def run_BGP(router_port, ttl, id, flag, router_table_name, socket):

    # Leer el archivo de rutas
    path = "tablas_de_rutas/" + router_table_name

    possible_next_hop_address = []
    possible_next_hop_routes = []
    known_ports = [router_port]

    with open(path, "r") as f:
        for line in f:
            _, rest = line.split(" ", maxsplit= 1)

            route, next_hop_ip, next_hop_port, _ = rest.rsplit(" ", maxsplit= 3)

            possible_next_hop_address.append((next_hop_ip, int(next_hop_port)))
            possible_next_hop_routes.append(route.split(" "))
            if int(next_hop_port) not in known_ports: 
                known_ports.append(int(next_hop_port))

        possible_next_hop_routes = [[int(port) for port in route] for route in possible_next_hop_routes]

        for address in possible_next_hop_address:
            # Enviar el mensaje BGP
            IP_packet = f"{address[0]},{address[1]},{ttl.zfill(3)},{(str(id)).zfill(8)},{(str(0)).zfill(8)},{(str(len('START_BGP'.encode()))).zfill(8)},{flag},START_BGP"
            socket.sendto(IP_packet.encode(), address)

    for address in possible_next_hop_address:
        # Enviar el mensaje BGP
        IP_packet = create_BGP_message(router_port, ttl, id, possible_next_hop_routes, address)
        socket.sendto(IP_packet.encode(), address)
        socket.settimeout(10)

    while True:
        try:

            # Recibir mensaje de actualizacion de rutas
            message, address = socket.recvfrom(1024)

            # Decodificar el mensaje
            decoded_message = message.decode().rstrip("\n")

            # Parsear el mensaje
            parsed_message = parse_packet(decoded_message.encode())

            # Revisar si el mensaje viene de un vecino chequear esto
            if parsed_message["port"] == router_port:

                # Revisar si el mensaje es de inicio de BGP
                if parsed_message["message"].startswith("START_BGP"):
                    continue

                # Revisar si el mensaje es de actualizacion de rutas
                if parsed_message["message"].startswith("BGP_ROUTES"):                    
                    # Obtener las rutas del mensaje
                    _, _, *asn_routes, _ = parsed_message["message"].split("\n")
                    
                    # Guardar las rutas en una lista
                    asn_routes_list = [route.split(" ") for route in asn_routes]
                    asn_routes_list = [[int(port) for port in route] for route in asn_routes_list]

                    update_routes = False

                    # Revisar si en el mensaje de rutas aparece este router                    
                    for route in asn_routes_list:
                        for port in route:
                            if port == router_port:
                                break
                        if route[0] not in known_ports:
                            # Agregar la ruta con el puerto a las rutas que se conocen
                            possible_next_hop_routes.append(route + [router_port])
                            known_ports.append(route[0])
                            update_routes = True

                        if route[0] in known_ports:
                            # Revisar si existe una ruta mas corta, y si existe, se reemplaza la ruta mas larga
                            for j in possible_next_hop_address:
                                if len(route) < len(j):
                                    j = route
                                    update_routes = True
                                    break
                        
                        if update_routes:
                            IP_packet = create_BGP_message(router_port, ttl, id, possible_next_hop_routes, address)
                            socket.sendto(IP_packet.encode(), address)


                            # Setear un timer
                            socket.settimeout(10)

        except TimeoutError:
            socket.settimeout(None)
            return possible_next_hop_routes