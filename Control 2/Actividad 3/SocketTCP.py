import socket
import random

class SocketTCP():

    def __init__(self):
        # Creando un socket no orientado a conexión
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.destinity_address = None
        self.origin_destiny = None
        self.secuence_number = None

    def parse_segment(self, tcp_segment):
        """ convierte un mensaje tcp con headers a un diccionario de:
            diccionario: head: {SYN: ,ACK: ,FIN: , seq: }, body: 

            tcp segment tiene el siguiente formato
               headers(0 o 1) ||| mensaje (string)
            SYN|||ACK|||FIN|||seq|||msg
        """

        tcp_dictionary = {}
        head, body = tcp_segment.rsplit(sep= "|||", maxsplit= 1)
        
        headers = head.split(sep= "|||", maxsplit= 3)
        # print(tcp_segment)
        headers = [int(x) for x in headers]
        
        headers_dictionary = {}
        for i in range(len(headers)):
            if i == 0:
                headers_dictionary.update({"SYN": headers[i]})
            if i == 1:
                headers_dictionary.update({"ACK": headers[i]})
            if i == 2:
                headers_dictionary.update({"FIN": headers[i]})
            if i == 3:
                headers_dictionary.update({"seq": headers[i]})
        
        tcp_dictionary.update({"headers": headers_dictionary})
        tcp_dictionary.update({"body": body})
        return tcp_dictionary

    def create_segment(self, parsed_tcp_message):
        """ convierte un diccionario de: diccionario: head: {SYN: ,ACK: ,FIN: , seq: }, body: 
            a un mensaje de este formato
            
            tcp segment tiene el siguiente formato
               headers(0 o 1) ||| mensaje (string)
            SYN|||ACK|||FIN|||seq|||msg
        """
        tcp_segment = ""
        for tcp_message, message in parsed_tcp_message.items():
            if tcp_message == "headers":
                for tcp_headers, headers in message.items():
                    tcp_segment += str(headers) + "|||"
            else:
                tcp_segment += message

        return tcp_segment


    def bind(self, address):
        # tener ojo con los address
        self.destinity_address = address

        self.socket.bind(address)

    def connect(self, address):
        self.secuence_number = random.randint(0, 100)

        message = "1|||0|||0|||" + str(self.secuence_number) + "|||"
        
        # chequear si se tiene que hacer bind a esta funcion, parece que no
        # self.socket.bind(address)
        self.socket.sendto(message.encode(), address)

        # por ahora se ocupa 20 pero deberia ser 15??
        message, server_address = self.socket.recvfrom(20)
        self.destinity_address = server_address

        parsed_message = self.parse_segment(message.decode())
        parsed_headers = parsed_message["headers"]

        if parsed_headers["SYN"]:
            if parsed_headers["ACK"]:
                if parsed_headers["seq"] == self.sequence_number + 1:
                    message = "0|||1|||0|||" + str(self.secuence_number + 2) + "|||"
                    # chequear si self.destiny_address es correcto o deberia ser address nomas
                    self.socket.sendto(message.encode(), self.destinity_address)

    def accept(self):
        
        message, client_address = self.socket.recvfrom(20)

        parsed_syn_message = self.parse_segment(message.decode())

        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        new_client_address = (client_address[0], int(client_address[1]) + 1)
        new_socket.bind(new_client_address)

        seq = 0
        if parsed_syn_message["headers"]["SYN"] == 1:
            parsed_syn_message["headers"]["seq"] += 1
            seq = parsed_syn_message["headers"]["seq"]
            message = self.create_segment(parsed_syn_message)
            new_socket.sendto(message.encode(), client_address)

        ack_message, _ = self.socket.recvfrom(20)

        parsed_ack_message = self.parse_segment(ack_message.decode())
        parsed_ack_header = parsed_ack_message["headers"]

        if parsed_ack_header["ACK"]:
            if parsed_ack_header["seq"] == seq + 1:
                print("final")
                return (new_socket,  new_client_address)
        