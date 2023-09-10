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

    """ header = parsed_messsage.header
    
    number_of_query_elements = header.q
    number_of_answer_elements = header.a
    number_of_authority_elements = header.auth
    number_of_additional_elements = header.ar

    q = {}

    q["header"] = [{"ancount": number_of_answer_elements}, 
                   {"nscount": number_of_authority_elements}, 
                   {"arcount": number_of_additional_elements}]

    if number_of_query_elements > 0:
        query = parsed_messsage.get_q()
        q["question"] = [{"qname": query.qname}]
    if number_of_answer_elements > 0:
        answer = parsed_messsage.rr # resource records
        q["answer"] = answer
    if number_of_authority_elements  > 0:
        authority = parsed_messsage.auth
        q["authority"] = authority
    if number_of_additional_elements > 0:
        additional = parsed_messsage.ar  
        q["additional"] = additional """

    return parsed_messsage

def part_b(answer):
    print("type")
    print(answer.rr.get_a().rtype)
    if (answer.rr.get_a().rtype == "A"):
        return 1

def resolver(mensaje_consulta):
    
    print("mensaje consulta")
    print(mensaje_consulta)
    parsed_message = parse_dns_message(mensaje_consulta)

    query = parsed_message.q.qname
    print("qname/query")
    print(query)

    # parte a
    answer = send_dns_message(query, ip_dns_address)

    print("answer")
    print(answer)

    # parte b
    if(answer.header.a > 0):
        if (part_b(answer) == 1):
            return answer
    # parte c
    if(answer.header.auth > 0):
        for j in answer.auth:
            if j.rtype == QTYPE.NS:
                for i in answer.ar:
                    if (i.rclass == "A"):
                        send_dns_message(query, i.ar[0].rdata)
                        break
                break
        else:
            recursive_name_server = answer.auth[0].rdata
            print("recursive name server")
            print(str(recursive_name_server.label).encode())
            solved_ip_message = resolver(str(recursive_name_server.label).encode())
            solved_dns_message = send_dns_message(query, solved_ip_message)
            if (part_b(solved_dns_message) == 1):
                return solved_dns_message

