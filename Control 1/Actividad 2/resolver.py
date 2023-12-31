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
 