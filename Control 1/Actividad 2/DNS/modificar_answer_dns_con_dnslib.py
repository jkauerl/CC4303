from dnslib.dns import RR, A
from dnslib import DNSRecord, DNSHeader, DNSQuestion

# Modificar el mensaje de pregunta (opción 1)
dns_query.add_answer(RR(qname, QTYPE.A, rdata=A(ip_answer)))

# Modificar el mensaje de pregunta (opción 2)
dns_query.add_answer(*RR.fromZone("{} A {}".format(qname, ip_answer)))

# Crear un nuevo mensaje que contenga la pregunta y la respuesta