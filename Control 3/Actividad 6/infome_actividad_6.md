# Informe Actividad 6: Fragmentación
# CC4303: Redes

Profesora: Ivana Bachmann
Auxiliar: Vicente Videla
Estudiante: Javier Kauer
Fecha de entrega: 25/11/2023

# Desarrollo

Para esta actividad se siguieron los pasos tal cual descrito en la sección de la activadad.

Se reutilizó el código de la actividad 5.

Tal como puede ser observado, esta actividad esta organizado tal como se dice a continuación. Un archivo llamda router.py, el cual contiene la implementación del router, un archivo utils.py, el cual contiene las funciones pedidas, también se incluye 3 archivos test.py con pruebas, y finalmente se tiene una carpeta con todas las tablas de rutas.

## Parte 1:

Durante esta parte, se módifico la función de parse_packet y create_packet para poder incluir los nuevos headers necesario para hacer esta actividad. Por lo tanto el código de ambas funciones termina siendo tal como se muestra a continuación.

``` python
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
```

Tal como se puede observar se sigue el mismo principio de la actividad pasada de guardar los valores en un diccionario y sino rescatarlos de este mismo y convertirlo en una string. Una observación importante coresponde a que se ocupa el método zfill para hacer padding de 0 antes del número establecido, esto porque es necesario para la actividad. Esto se aplico para: ttl, id, offset, y size.

Después se ocupa el archivo test1.py para ver si se ejecuta correctamente las funciones.

## Parte 2:

En este paso se modificá la función de check_routes para poder extraer el mtu desde el archivo de rutas. A continiación se presenta el código actualizado.

``` python
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
```

Tal como se puede observar, ahora se retorna un par que contiene: un par de la dirección y el mtu de la ruta. Para hacer esto, cuando se hace split de la linea se agrega un valor más que corresponde al mtu.

## Parte 3:

En esta parte se crea la función fragment_IP_packet(IP_packet, MTU), la cual recibe el paquete IP y el mtu, y verifica si se tiene que fragmentar el mensaje o no, retornando una lista con los mensajes resultantes. A continuación se muestra la implementación.

``` python
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
```

Tal como se puede observar, la función primero revisa si todo el mensaje cabe dentro del mtu, y si es así, entonces retorna el mensaje de forma instantánea. Si no se cumple la condición, entonces de forma iterativa va fragmentando el mensaje agregando correctamente los headers a los mensaje y se van agregando a una lista que la retorna. Es importante mencionar que para logra esto, se ocupa una implementación iterativa, es decir que primero calcula la cantidad del mensaje que se puede enviar inclueyndo los headers por la ruta, y luego de va obteniendo splices de ese tamaño para crear el mensaje. Además calcula automáticamente el offset y el size del mensaje que se esta enviado. Finalmente si este corresponde a el final, entonces incluye el header adecuadamente, y si se tiene que fragmentar el último mensaje mueve el flag 0 hasta el final.

Para probar el funcionamiento correcto se corre el script de test2.py modificando los valores de mtu y el mensaje que se quiere enviar.

## Parte 4:

En esta sección se actualiza el código de router.py para fragmentar correctamente el mensaje en la ruta que se esta enviado el mensaje. El código se muestra a continuación.

``` python
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
```

Tal como se puede observar, se obtiene el mtu de la ruta seleccionada y se ocupa la función de esta sección para fragmentar el mensaje. Finalmente se envia de forma iterativa los mensajes por esa ruta.

### Parte 5:

En esta parte se programa la función reassemble_IP_packet(fragment_list). Esta función recibe una lista de fragmentos y reconstruye el mensaje siguiendo ciertas reglas para finalmente retornarlo. A continuación se muestra la implementación de la función.

``` python
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
```
Esta función primero recibe si el contenido del mensaje esta vacio o no, y si es así entonces retorna None. Después parsea la lista y verifica si tiene un elemento, y si es así entonces retorna el mensaje de una si el flag es 0. Si no es así, entonces ordena el mensaje en función del offset de cada mensaje. A continuación hace una verificación preliminares con respecto a si el primer elemento no tiene offset 0 y si el último elemento no tiene flag 0, lo cual causa que retorne None. Una vez hecho esta trata de asemblar el mensaje agregando la sección del mensaje en una string, además comprueba que el offset sea el correcto para saber si un mensaje se perdió, esto se hace menteniendo un contandor del size del mensaje y comprobandoló con el offset del fragmento, y si no es así retorna None. Finlamente si todo esta correcto retorna el mensaje con los headers adecuados. 

Para probar que esto funciona se ocupa el archivo test3.py el cual verifica que este reensamblando los fragmentos correctamente.

### Parte 6:

En esta seccción se implementa el uso de un diccionario que almacena los mensajes recibido con respecto a un id. El código de la implementación se encuentra a continuación.

```python
# Diccionario con mensajes fragmentados
dict_of_fragments = {}
```

``` python

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
```

Tal como se puede observar se hacen 2 importantes modificaciones, la primera corresponde al primer código que se muestra, lo cual es una variable global de un diccionario que siempre se conoce. La segunda moficación corresponde al uso del diccionario para constantemenete actualizar los fragmentos que llegan, y después los fragmentos se guardan en una lista haciendo uso del id obtenido del mensaje.

### Parte 7:

Finalmente, en esta parte se trata de reensamblar el mensaje cada vez que llegan un nuevo fragmento. La implementación se muestra a continuación.

``` python
fragmented_list = [create_packet(fragment).encode() for fragment in parsed_fragmented_list]

# Tratar de rearmar el paquete
reassembled_IP_packet = reassemble_IP_packet(fragmented_list)

# Caso en donde no se puede rearmar el paquete
if reassembled_IP_packet == None:
    continue

message = parse_packet(reassembled_IP_packet.encode())["message"]
```

Tal como se puede observar, este código primero parsea los mensajes almacenados en la lista de la parte anterior, y después se llama a la función de reensamblaje recibiendo la lista de los fragmentos. Finalmente si esta función retorna None, entonces se vuelve a esperar un nuevo mensaje, y si retorna algo, imprime el mensaje.

## Pruebas

### Parte 1:

Ocupando la red de 5 routers, se envia un mensaje con un ttl de 10, y se observa que los routers correctamente descartan los mensaje con ttl igual a 0.

### Parte 2:

Ocupando el último mensaje en el archivo prueba.py, se crea una red con 5 routers, y se envia este mensaje con largo de 150 bytes entre distintos routers, observa que el camino es distinto para cada vez, pero que el router de destino correctamente reensambla los mensaje una vez que se reciben todos los mensaje. Es importante mencionar que se hacen recorrido poco eficientes, pues esto se demorán más tomando una camino más largo que otro posible camino. Además se observa que el código logra fragmentar fragmentos cuando es necesario.