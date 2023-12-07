from math import ceil

# Funciones de utilidad

round_robin = []

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
            return create_packet(parsed_fragment_list[0])
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
