# Funciones de utilidad

round_robin = []
# two = 0

def parse_packet(IP_packet):
    decoded_IP_packet = IP_packet.decode()

    # Obtener los valores de la IP, puerto y mensaje
    ip, port, ttl, message = decoded_IP_packet.split(",", maxsplit=4)

    # Guardar los valores en un diccionario
    parsed_packet = { "ip": ip, "port": int(port), "ttl": int(ttl), "message": message}
    return parsed_packet

def create_packet(parsed_packet):

    # Rescatar los valores del diccionario
    ip = parsed_packet["ip"]
    port = parsed_packet["port"]
    message = parsed_packet["message"]
    ttl = parsed_packet["ttl"]

    # Crear el paquete IP y retornarlo
    IP_packet = f"{ip},{port},{ttl},{message}"
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
        possible_next_hop_address = []
        possible_next_hop_index = []


        f.seek(0)
        # Ir chequeando linea por linea las rutas disponibles
        for line in f:
            _, start_port, end_port, next_hop_ip, next_hop_port = line.split(" ")

            # Si la dirección de destino está en el rango de puertos de la ruta, se agrega a la lista de posibles puertos
            if destination_address[1] >= int(start_port) and destination_address[1] <= int(end_port):
                possible_next_hop_address.append((next_hop_ip, int(next_hop_port)))
                possible_next_hop_index.append(line_counter)

            line_counter += 1

        # Si hay posibles puertos, se escoge el que tenga menos paquetes enviados
        if possible_next_hop_address != []:
            
            # Inicializar los valores de la primera ruta como el mínimo
            next_hop_ip = None
            next_hop_port = None

            min_round_robin = 10000
            min_round_robin_index = 0

            # Recorrer los valores de las rutas posibles y escoger la que tenga menos paquetes enviados
            for i in range(len(possible_next_hop_address)):
                if round_robin[possible_next_hop_index[i]] < min_round_robin:
                    min_round_robin = round_robin[possible_next_hop_index[i]]
                    min_round_robin_index = possible_next_hop_index[i]
                    next_hop_ip = possible_next_hop_address[i][0]
                    next_hop_port = possible_next_hop_address[i][1]

            # Actualizar el valor de paquetes enviados
            round_robin[min_round_robin_index] += 1
            return (next_hop_ip, next_hop_port)
        else:
            return (None, None)