from utils import *

mtu = 51

IP_packet_v1 = "127.0.0.1,8881,010,00000347,00000000,00000007,0,hola!ab".encode()
print(IP_packet_v1)
fragment_list = fragment_IP_packet(IP_packet_v1, mtu)
print(fragment_list)
IP_packet_v2_str = reassemble_IP_packet(fragment_list)
IP_packet_v2 = IP_packet_v2_str.encode()
print(IP_packet_v2)
print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))