#              ACK  SYN  FIN  seq   msg  
""" tcp_message = "0|||0|||0|||0|||"

parsed_tcp = tcp_message.rsplit(sep= "|||", maxsplit= 1) """
# headers = head.split(sep= "||", maxsplit= 3)
# headers = [int(x) for x in headers]

# headers_dict = {"test": 1, "test2": 2}



# print(len(headers_dict))
# print(list(headers_dict.values())[0])

tcp_message = "tcp message"


print(tcp_message)

print(tcp_message[0:11])
print(tcp_message[11:] == "")
