import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

ip_dns_address = "192.33.4.12"

def send_dns_message(query, ip):
    # Acá ya no tenemos que crear el encabezado porque dnslib lo hace por nosotros, por default pregunta por el tipo A
    # qname = query["question"][0]["qname"]
    q = DNSRecord.question(query)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # lo enviamos, hacemos cast a bytes de lo que resulte de la función pack() sobre el mensaje
        sock.sendto(bytes(q.pack()), (ip_dns_address, 53))
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

    header = parsed_messsage.header
    
    number_of_query_elements = header.q
    number_of_answer_elements = header.a
    number_of_authority_elements = header.auth
    number_of_additional_elements = header.ar

    q = {}

    q["header"] = [{"ancount": number_of_answer_elements}, {"nscount": number_of_authority_elements}, 
                   {"arcount": number_of_additional_elements}]

    if number_of_query_elements > 0:
        query = parsed_messsage.q
        q["question"] = [{"qname": query.qname}]
    if number_of_answer_elements > 0:
        answer = parsed_messsage.rr # resource records
        q["answer"] = answer
    if number_of_authority_elements  > 0:
        authority = parsed_messsage.auth
        q["authority"] = authority
    if number_of_additional_elements > 0:
        additional = parsed_messsage.ar  
        q["additional"] = additional

    print(q)
    return q

def resolver(mensaje_consulta):
    
    parsed_message = parse_dns_message(mensaje_consulta)

    query = parsed_message["question"][0]["qname"]

    response_message = send_dns_message(query, ip_dns_address)

    if (response_message.rtype == "A"):
        return response_message
    elif (response_message["authority"]["rtype"] == "NS"):
        for i in response_message["additional"]["rtype"]:
            if (i == "A"):
                send_dns_message(query, response_message["additional"][0]["rdata"])
        else:
            recursive_name_server = response_message["authority"][0]
            solved_ip_message = resolver(recursive_name_server)
            send_dns_message(query, solved_ip_message)
