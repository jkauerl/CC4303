from utils import *

mtu = 51

IP_packet = "127.0.0.1,8881,010,00000347,00000000,00000007,0,hola!ab".encode()
IP_packet_fragmented = fragment_IP_packet(IP_packet, mtu)
print(IP_packet_fragmented)