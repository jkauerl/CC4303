# Informe Actividad 5: Forwaring
# CC4303: Redes

Profesora: Ivana Bachmann
Auxiliar: Vicente Videla
Estudiante: Javier Kauer
Fecha de entrega: 25/11/2023

# Desarrollo

Para esta actividad se siguieron los pasos tal cual descrito en la sección de la activadad.

Además se utilizacon las siguiente librería: sockets y sys.

Tal como puede ser observado, esta actividad esta organizado tal como se dice a continuación. Un archivo llamda router.py, el cual contiene la implementación del router, un archivo utils.py, el cual contiene las funciones pedidas, un archivo prueba_router.py, el cual contiene una prueba, un archivo archivo_prueba.txt, el cual contiene un texto de prueba, también se incluye 2 archivos test.py con pruebas, y finalmente se tiene una carpeta con todos las tablas de rutas.

## Mini-Internet sin TTL:

Durante esta sección se implementó las funciones pedidas considerando un internet sin ttl.

Tal como se puede observar, las diferencias y similitudes que se tienen con las tablas de rutas de la actividad y tablas de rutas reales son las siguientes. En referencia a diferencias, las principales corresponden a que en el real el destino y el origen se expresan con la dirección IP, mientras que la de la actividad ocupa los puertos para simular. Además, los puertos se ocupan para distinguir los procesos, mientras que en la actividad corresponden a la ubicación del router. Con respecto a las similitudes, en ambos se ocupa una conexión de punta a punta, es decir que solamente se tiene los vecinos diretos entre distintos routers.

### Paso 2:

A continuación se implementa la funcionalidad para que en el archivo router.py se pueda recibir los paramentros, usando la librería sys, de ip, puerto y nombre de tabla de rutas, al correr el script. El código se encuentra a continuación:

``` python
import sys
import socket
from utils import *

# Rescatar los valores al invocar el script
router_ip = sys.argv[1]
router_puerto = int(sys.argv[2])
router_table_name = sys.argv[3]
```

Tal como se puede ver se guardan los valores en las variables correspondientes.

### Paso 3:
En este paso, se implementa un socket, usando la librería socket, en forma no bloqueante que esta vinculado con el ip y puerto obtenido en el par anteriormente. La implementación de esto se encuentra a continuación.

``` python
# Creación del socket no orientado a conexion
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bloquear el socket y hacer que escuche en el puerto correctamente
udp_socket.bind((router_ip, router_puerto))
udp_socket.setblocking(True)
```

### Paso 4:

A continuación se implementa la función de parse_packet(IP_packet) y create_packet(parsed_IP_packet). Estas funciones sirven para parsear un mensaje IP almacenando los valores en un diccionario con su llave correspondiente, y del diccionario mencionado anteriormente rescatar los valores y armar el mensaje IP. La implementación de esto se encuentra a continuación, la cual se encuentra en el archivo utils.py.

``` python
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
```

Para probar el funcionamiento correcto de esto se correr el archivo test1.py

### Paso 5:

En este paso, se implementa la fucion check_route(routes_file_name, destination_address). Esta función recibe la tabla de rutas del router correspondiente y la dirección de destino para retornar el par (next_hop_IP, next_hop_puerto), el cual corresponde al primer router que se encuentra en la tabla de rutas para enviar el mensaje recibido y hacer forwarding. La implementación se encuentra en el archivo utils.py y se muestra a continuacón

``` python
round_robin = []

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
```

Tal como se puede observar primero se lee la tabla de rutas, y se va iterando las lineas leidas para obtener el primer rango de puertos en donde se encuentra el puerto al cual se tiene que enviar el mensaje. Finalmente, si no se encuentra un puerto, este retorna el par None, None pues no se tiene una ruta hacia ese destino.

Para probar el funcionamiento correcto de este se corren 4 terminales, las primeras 3 para el router 1, 2 y 3, y el último para enviar el mensaje 127.0.0.1,8884,hola al puerto 1 usando netcat.

### Paso 6

En este paso se implenta la funcionalidad del router para recibir mensajes en un loop. Además se comprueba el contenido del mensaje para saber si este; es una mensaje al router, un mensaje que se tiene que hacer forwaring, o si no se tienen rutas hacia ese router. La implementación de este código se encuentra a continuacón.

``` python
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
```

Tal como se puede observar, se observa la presencia de un loop while True, el cual corresponde al comportamiento de recibir mensajes continuamente. También se ocupa las funciones creadas en el paso 4 para parsear el mensaje recibido, y crear el mensaje para hacer forwaring. También se verifica si el destino del mensaje corresponde a el router y si lo es se imprime el mensaje. Además se verifica si se tiene que ahcer forwaring, y si es así, entonces se invoca la función programada en la parte 5 para obtener el router que se le hace forwaring.

### Parte 7: 

En esta parte se envía mensajes en la red descrita en esta parte. Dentro de los interesante se observa que existe un loop infinito entre el router R2 y el router R3. Esto porque como el primer router de forwaring son el otro router, se envia y reenvia continuamente el mensaje entre ellos 2.

### Parte 8:

Para esta parte se implementa la funcionalidad de round robin entre los distintos routers. Es decir que si existen más de 2 rutas posibles, entonces se envía al router por turnos, en otras palabras se envía al que menos ha enviado mensajes.

Para lograr esto se ocupa una lista llamda round_robin que almacena la cantidad de mensajes que se han enviado por un router. Además, para logra esto, cuando se chequea los routers posibbles se crean 2 listas, una de la dirección posible que se puede tener, y otra con el índice de esta dirección en la tabla de rutas. De esta forma se puede verificar directamente ocupando la lista de indices el router que menos mensajes se enviado directamente de la variable round_robin, y cuando se obtiene el valor se envia el mensaje por ese router y se aumenta la cantidad de mensajes enviados por ese router en 1. Para lograr esto correctamente se tiene que usar la keyword global antes de usar round_robin, puesto que el módulo utils se importa en router.py.

Después de implementar esto se corren 2 tests, el primero corresponde a rehacer el test de la parte 7, y se observa que el router 5 recibe correctamente el enviado a el router 1. El segundo test corresponde a agregar 2 routers más en la red, el router 0 conectado a el router 1 y 2, y el router 6 conectado a el router 2 y 3. Se verifica correctamente que el router 2 hace correctamente round robin.

### Parte 9:

Para completar correctamente esta parte, se tiene que agregar una nueva tabla de ruta para el router default, y actualizar las tablas de rutas para los routers ya existentes. 

Como corresponde al router default, las tablas de rutas corresponden a enviar todos los mensajes con destino a la red hacia cualquier router de la red, y sino solamente se recibe. La siguiente tabla corresponde a la tabla de ruta de este router.

``` text
127.0.0.1 8880 8886 127.0.0.1 8881
127.0.0.1 8880 8886 127.0.0.1 8882
127.0.0.1 8880 8886 127.0.0.1 8883
127.0.0.1 8880 8886 127.0.0.1 8884
127.0.0.1 8880 8886 127.0.0.1 8885
127.0.0.1 8880 8886 127.0.0.1 8886
```

Para la tabla de ruta de los routers de ejemplo, se tiene que agregar una linea con los destinos de 0 hasta el puerto antes de la red, y otra linea con 1 más del puerto mas grande hasta el infinit. Además no importa la ubicación de la ruta pues esta se verifica con la implementación de round robin. A continuacón se muestra una tabla de ruat de ejemplo.

``` text
127.0.0.1 0 8879 127.0.0.1 7000
127.0.0.1 8881 8886 127.0.0.1 8881
127.0.0.1 8881 8886 127.0.0.1 8882
127.0.0.1 8887 100000 127.0.0.1 7000
```

## Mini-Internet con TTL:

### Parte 1:

Se modifica la función de parse_packet y create_packet considerando que se tiene un ttl.

### Parte 2:

En el paso 6 de la sección anterior se puede observar como se hace el caso cuando el ttl recibido corresponde a un valor igual a 0. En donde simplemente descarta el valor obtenido y se imprime en pantalla el mensaje descartado.

### Parte 3:

Nuevamente en el paso 6 de la sección anterior se observa que cuando se recibe un mensaje, se decrementa el valor del ttl en 1 luego de hacer forwaring.

## Parte 4:

En esta sección se crea el archivo prueba_router.py el cual corresponde a leer una archivo, encapsularlo en headers IP, y luego envia linea por linea el mensaje. El código de este arhcivo se encuentra a continuación.

```python
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
```

# Pruebas

## Mini-Internet sin TTL:

### Parte 1:

Al cambiar la configuración de la tabla de ruta del router 2 por la indica en la activdad, se observa que existe un loop infinito entre el router 1 y el router 2. 

## Parte 2:

Después de correr el test contimunatmente, se ve que los saltos que se hacen se hacen de una forma predictiva, esto porque siempre se tiene en consideración el round robin al momento de hacer los saltos, causando que si bien parezvan aleatorios los saltos, esto se hacen de una forma controlada considerando la funcionalidad de round robin.

## Parte 3:

Al igual que en el caso anterior, se observa el mismo comportamienteo anteriormente descrito pero con una red más grande. Por lo tanto se puede observar que el comportamiento obtenido es complemtamente predictivo si se considera todos los casos.


## Mini-internet con TTL:

### Parte 1:

La diferencia principal que se ve corresponde que luego de 10 intercambios entre el router 1 y el router 2, se descarta el mensaje y se espera recibir otro mensaje para o ser recibido y para hacer forwaring.

### Parte 2:

Se observa que luego de crear el archivo prueba_router.py se envia, se hace forwaring, y se recibe correctamente todos los mensajes enviados a través de la red.

### Parte 3:

Se observa que luego de enviar un archivo grande, los mensaje recibido por el router del destino se encuentran desordenados, puesto que como se hace round robin, puede que paquetes que se enviaron primeros lleguen después de otros porque toman un camino más largo.