def resolver(mensaje_consulta, debug=False):

    root_dns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    root_dns_sock.sendto(mensaje_consulta, ROOT_DNS_SERVER)
    response, _ = root_dns_sock.recvfrom(4096)

    parsed_response = parse_dns_msg(response)
    
    if (len(parsed_response["Answer"]) > 0):
        if parsed_response["Answer"]["answer_type"] == 'A':
            return response

    if (len(parsed_response["Authority"]) > 0):
        if (parsed_response["Authority"]["auth_type"] == 'NS'):
            if (len(parsed_response["Additional"]) > 0):
                for i in parsed_response["Additional"]["additional_records"]:
                    if QTYPE.get(i.rclass) == 'A':
                        server_ip = str(parsed_response["Additional"]["first_additional_record_rdata"])
                        if debug:
                            print(f"(debug) Consultando '{parsed_response['Qname']}' a '{parsed_response['Additional']['first_additional_record_rname']}' con dirección IP '{server_ip}'")
                        dns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        dns_sock.sendto(mensaje_consulta, (server_ip.encode(), 53))
                        responseq, _ = dns_sock.recvfrom(4096)
                        return responseq
                    
                name_server = str(parsed_response["Authority"]["name_server_domain"])
                if debug:
                    print(f"(debug) Consultando IP para '{name_server}' (Name Server)...")
                query = DNSRecord(DNSHeader(qr=0, opcode=0, aa=0, tc=0, rd=1), q=DNSQuestion(name_server, QTYPE.A)).pack()
                resolver(query, debug=debug)                
    return b