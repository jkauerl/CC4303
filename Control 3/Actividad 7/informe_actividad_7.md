# Informe Actividad 7: BGP
# CC4303: Redes

Profesora: Ivana Bachmann
Auxiliar: Vicente Videla
Estudiante: Javier Kauer
Fecha de entrega: 25/11/2023

# Desarrollo

Para esta actividad se siguieron los pasos tal cual descrito en la sección de la activadad.

Se reutilizó el código de la actividad 6.

Tal como puede ser observado, esta actividad esta organizado tal como se dice a continuación. Un archivo llamda router.py, el cual contiene la implementación del router, un archivo utils.py, el cual contiene las funciones pedidas, y finalmente se tiene una carpeta con todas las tablas de rutas.

## Parte 1:

En esta parte se crea la función create_BGP_message(), la cual recibe todos los parámetros necesario para hacer un mensaje con las rutas. La implementación se muestra a continuación.

``` python
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
```

Tal como se puede observar, esta función recibe el puerto del router, el ttl, el id, las actuales rutas conocidas, y la dirección de destino. Primero, crea una lista con los posibles routers, después los convierte en enteros, a continuación empieza a crear el mensaje con el formato indicado, es decir el mensaje de que corresponde a las rutas, después el puerto de origen, después todas las rutas separadas con un salto de linea, y finalmente el termino del mensaje. 

Para probar esto se ocupa el archivo de test.py el cual muestra si se crea un mensaje BGP correctamente.

## Parte 2:

En esta parte se modifica el código que se tenía originalmente para ver si el mensaje recibido corresponde a un mensaje de comienzo del algoritmo BGP. A continuación se muestra la implementación.

``` python
# Caso en donde el mensaje es un mensaje de inicio de BGP
if parsed_message["message"].startswith("START_BGP"):
    updated_routes = run_BGP(router_puerto, parsed_message["ttl"], parsed_message["id"], parsed_message["flag"], router_table_name, udp_socket)
```

Tal como se puede observar, primero, se verifica que el mensaje comienze con START_BGP, y si es así, corre el algoritmo de run_BGP(). 

## Parte 3:

Esta sección corresponde a crear el algoritmo BGP el cual se muestra en la actividad. Esta función tiene el propósito de actualizar las rutas entre los distintos routers de forma dinámica mediante compartiendo las rutas que se conocen a sus vecinos, y ellos actualizando correctamente las rutas agregandose a si mismo al final. A continuación se muestra la implementación de la función.

``` python
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
```

Tal como se puede observar, se muestra el algoritmo BGP. Primero la función abre las rutas que se conocen y estas se guardan en distintas listas, almacenando también los puertos que se conocen y finalmente se envia un mensaje de inció de BGP a los vecinos a este router. Después se envía un mensaje que contiene las rutas que se conoce al comenzar el algoritmo a los vecinos y se pone un timer. Después se entra en un loop while True, con un try y except. A continuación se reciben los mensaje, se parsea, y se revisa el contenido del mensaje para saber si es una mensaje BGP. Si es así entonces se obtiene las rutas que conoce el vecinos, y entonces se hacen las verificaciones para ver si se tiene que agregar la ruta. Primero se verifica si hay un puerto que se conoce, y si es así se hace break, después se comprueba si el puerto de destino se conoce, y si no es así, entonces se agrega la ruta a las rutas conocidas, y se agrega el puerto del router al final. Si no se cumple la condición anterior, entonces se comprueba con las rutas que se tiene para saber si esta es una ruta más corta, y si es así la reemplaza y si no, la ignora. Finalmente, se modifica una variable que almacena si se cambió una ruta y si es así, entonces se envía las rutas actualizadas a los vecinos. Finalmente, cada vez que se envía una mensaje a un vecino se resetea el timer a 10 segundos, y una vez pasados los 10 segundo se quita el timer, y se retorna las rutas actualizadas en una lista.

Finalmente, se comprueba que se cumple el intercambio de rutas corriendo ocupando una configuración del 3 routers.

## Parte 4

Finalmente, se modifica el código para que se imprime las rutas actualizadas, y las guarde en un archivo. El códigod se muestra a continuación.

``` python
updated_routes = run_BGP(router_puerto, parsed_message["ttl"], parsed_message["id"], parsed_message["flag"], router_table_name, udp_socket)

updated_routes_string = [f"{' '.join(map(str, route))}" for route in updated_routes]
print(updated_routes_string)

# Leer el archivo de rutas
path = "tablas_de_rutas/" + router_table_name

with open(path, "w") as file:

    message = ""

    for i, route in enumerate(updated_routes_string):
        message += f"{parsed_message['ip']} {route} {parsed_message['ip']} {updated_routes[i][-2]} {1000}\n"

    message = message.strip("\n")

    # Write content to the file
    file.write(message)

continue
```

Para hacer esto, primero se guarda lo que retorna la función run_BGP, después se convierte las rutas en una lista con string y se imprime. Finalmente, se guarda el archivo en la tabla de rutas que se pone al invocar la función, precoupandose en mantener el formato de las tablas de ruta.

Finalmente se comprueba el funcionamiento ocuando una configuración de 5 routers, y se utiliza las tablas de rutas version 2.

# Pruebas

## Parte 1:

Para hacer esta prueba, se ocupa las tablas de rutas version 3, corriendo los 7 routers, y enviando un mensaje para comenzar el algoritmo BGP. Después de terminar el proceos se comprueba que las tablas de rutas tienen rutas hacia todos los routers.

## Parte 2:

Después de modificar las tablas de rutas, y enviar un mensaje a los routers, se observa que existe un pequeño problema, pues las funciones de envió de mensaje no tienen en consideración el nuevo formato de las tablas de las tablas de ruta. Esto porque cuando se lee las tablas de rutas, estas las hacen considerando que existen 2 valores para los puertos, y no una cantidad mayor. Por lo tanto se tendría que modificar el desempaquetamiento de los puertos.

## Part 3:

Pueda hacer que no incluya a el router 4 como una de las direcciónes finales a las que se puede llegar. Porque de esta forma causa que no le llegue al router 4 un mensaje con el puerto de origen el router 7. 

