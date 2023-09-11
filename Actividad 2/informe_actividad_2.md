# Informe Actividad 2: construyamos un resolver
# CC4303: Redes

Profesora: Ivana Bachmann
Auxiliar: Vicente Videla
Estudiante: Javier Kauer
Fecha de entrega: 10/09/2023

## Desarrollo

En esta actividad se siguieron los pasos descritos en eol.

Para comenzar se crea un documento llamado *resolver.py* el cual recibe mensajes DNS. Aquí se creo un socket no orientado a conexión, y se ocupó la dirección localhost y el puerto 8000.

El código para implementar esto se encuentra a continuación:

```python
import socket
from utils import *

dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

dns_address = ("localhost", 8000)

dns_socket.bind(dns_address)
count=0
while(True):
    try:
        message, address = dns_socket.recvfrom(4096)
        
        parsed_message = parse_dns_message(message)
        solved_message = resolver(message, True)
        if (solved_message != None):
            dns_socket.sendto(solved_message.pack(), address)
    except KeyboardInterrupt:
        break
dns_socket.close()
```

Después se tenía que crear una función que parsea mensajes DNS. Con el principal objetivo de almacenar la información importante de este. Para lograr esto se creo la función *parse_dns_message(message)*, además se aprovecho de la funcionalidad de la librería de DNSLib la cual ya tiene un método integrado de parseo, y se almacena la información en las clases correspondiente. Estas son, DNSHeader, DNSRecorder, y DNSQuestion entre varías más. A continuación se muestra el código de esta función.

```python
def parse_dns_message(message):
    parsed_messsage = DNSRecord.parse(message)

    return parsed_messsage
```

La siguiente parte de la actividad corresponde a crear un resolver de dominions DNS. Para lograr esto se creó 2 funciones, una siendo la principal llamda *resolver(mensaje_consulta, debug, cache)*, y una función auxiliar llamada *part_b(answer, query, mensaje_consulta, debug, cache= [])*. Esta función resuelve trata de resolver de forma recursiva un dominio con el objetivo de retornar una respuesta para que lo reciba el cliente. El código se puede encontrar a continuación.

```python
ef part_b(answer, query, mensaje_consulta, debug, cache= []):
    # parte b
    if(answer.header.a > 0):
        if (answer.get_a().rtype == QTYPE.A):
            return answer
    # parte c
    if(answer.header.auth > 0):
        for j in answer.auth:
            if j.rtype == QTYPE.NS:
                for i in answer.ar:
                    if (i.rclass == QTYPE.A):
                        response = send_dns_message(query, str(i.rdata))
                        return response
        else:
            recursive_name_server = str(answer.auth[0].rdata.label)
            for i in cache:
                if i.keys == recursive_name_server:
                    part_b(cache[i], query, mensaje_consulta, debug, cache)
            question = DNSRecord.question(recursive_name_server)
            solved_ip_message = resolver(question.pack())
            add_item({ recursive_name_server: solved_ip_message})
            if debug:
                print(("(Debug) '{}' a '{}' con direccion IP '{}'").format(recursive_name_server, question, solved_ip_message))
            part_b(solved_ip_message, query, mensaje_consulta, debug, cache)
    return None

def resolver(mensaje_consulta, debug=False, cache=[]):
    
    parsed_message = parse_dns_message(mensaje_consulta)

    if cache:
        print("Se esta usando el cache")    

    query = parsed_message.q.qname

    # parte a
    answer = send_dns_message(query, ip_dns_address)

    #parte b y c
    resolver_answer = part_b(answer, query, mensaje_consulta, debug, cache)

    return resolver_answer
```

Finalmente se implementó la funcionalidad de usar una opción de debug, y una opción de cache. Esto se puede observar en las funciones anteriores en donde se ocupan los parametros *debug* y *cache*. El objetivo de esto es poder que un administrador observer las consultas que se hace el resolver de forma recursiva con su dominio y a que dirección ip. También hace que se pueda tener memoria de dominios que estan siendo frecuentemente consultados. Para lograr esto último se creó funciones adicionales que ayudan con este problema y se usó la librearía *collections* para facilitar las limitaciones de este cache. El código se pueden encontrar a continuación.

```python
from collections import deque
max_size = 20

cache = []

insertion_order = deque()

def add_item(item):
    cache.append(item)
    insertion_order.append(item)
    if len(cache) > max_size:
        # If the list exceeds the maximum size, remove the oldest item
        oldest_item = insertion_order.popleft()
        cache.remove(oldest_item)
```

## Resutados obtenidos

Una vez programado los todo lo requerido por la actividad. Se decidió ejecutar las pruebas para la funcionalidad correcta.

Para el primer test en donde se pide consultar el dominio de eol.uchile.cl se obtiene *;; Warning: ID mismatch: expected ID 59284, got 21130*.

Para el segundo test, se obtiene *; Warning: ID mismatch: expected ID 25990, got 50625*.

Para el tercer test se obtiene *;; Warning: ID mismatch: expected ID 31075, got 8258*

Finalmente, para el cuarto test se obtiene *;; Warning: ID mismatch: expected ID 55347, got 20550*.

Al tratar de resolver el dominio *www.webofscience.com* no se obtiene respuesta pues se queda en loop. La posible razón de porque esta sucediendo este comportamiento es por la implementación que se hizo, pues no se esta considerando los servidores de tipo IPv6, por lo tanto no se manejan correctamente este tipo de name servers. Por lo tanto para arreglar este problema sería que el resolver manejara este tipo de dominios. Ademmás al consultar el dominio de *www.cc4303.bachmann.cl*, no se nota cambio comparado con simplemente consultar con el resolver de google.

Finalmente, al hacer las consultas a un mismo dominio se puede observar que no se consulta a los mismo sitios y en el mismo orden. La razón de esto puede ser por como el protocolo DNS maneja las consultas con el objetivo de evitar la sobrecarga de esto.