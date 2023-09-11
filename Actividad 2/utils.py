import socket
from dnslib import DNSRecord, RR
from dnslib.dns import QTYPE
import dnslib
from collections import deque

ip_dns_address = "192.33.4.12"
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

def send_dns_message(query, ip):
    # Acá ya no tenemos que crear el encabezado porque dnslib lo hace por nosotros, por default pregunta por el tipo A
    # qname = query["question"][0]["qname"]
    q = DNSRecord.question(query)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # lo enviamos, hacemos cast a bytes de lo que resulte de la función pack() sobre el mensaje
        sock.sendto(bytes(q.pack()), (ip, 53))
        # En data quedará la respuesta a nuestra consulta
        data, _ = sock.recvfrom(4096)
        # le pedimos a dnslib que haga el trabajo de parsing por nosotros 
        d = DNSRecord.parse(data)
    finally:
        sock.close()
    # Ojo que los datos de la respuesta van en en una estructura de datos
    return d

def parse_dns_message(message):
    parsed_messsage = DNSRecord.parse(message)

    return parsed_messsage

def part_b(answer, query, mensaje_consulta, debug, cache= []):
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
    print(answer)

    #parte b y c
    resolver_answer = part_b(answer, query, mensaje_consulta, debug, cache)

    return resolver_answer

