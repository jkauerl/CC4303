import socket
from dnslib import DNSRecord
from utils import *

dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

dns_address = ("localhost", 8000)

dns_socket.bind(dns_address)

while(True):
    try:
        message, _ = dns_socket.recvfrom(4096)

        parsed_message = parse_dns_message(message)
        print(parsed_message)
    except KeyboardInterrupt:
        break
dns_socket.close()
