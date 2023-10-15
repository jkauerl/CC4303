#              ACK  SYN  FIN  seq   msg  
tcp_message = "0|||0|||0|||0|||msg"

parsed_tcp = tcp_message.rsplit(sep= "|||", maxsplit= 1)
# headers = head.split(sep= "||", maxsplit= 3)
# headers = [int(x) for x in headers]

headers_dict = {"test": 1, "test2": 2}



print(len(headers_dict))
print(list(headers_dict.values())[0])
