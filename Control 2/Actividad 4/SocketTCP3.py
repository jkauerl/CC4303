import socket
import random
from socketUDP import SocketUDP
import slidingWindowCC as swcc
import timerList as tl
from congestionControl import CongestionControl

random.seed(3)

udp_buff_size = 18 + 16

class SocketTCP():

    def __init__(self):
        # Creando un socket no orientado a conexión
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket = SocketUDP()
        self.socket.send_loss_rate = 0 # configurable
        self.destinity_address = None
        self.origin_destiny = None
        self.sequence = None
        self.rest = 0
        self.message_length = None
        self.cache = ""
        self.finished = False

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
                for _, headers in message.items():
                    tcp_segment += str(headers) + "|||"
            else:
                tcp_segment += message

        return tcp_segment

    def bind(self, address):
        # tener ojo con los address
        
        self.socket.bind(address)

    def connect(self, address):
        # se inicia un numero de secuencia aleatorio
        self.sequence = random.randint(0, 100)

        while True:
            try:
                self.socket.settimeout(5)
                # se crea el mensaje de sincronizacion y se manda
                message = b"1|||0|||0|||" + str(self.sequence).encode() + b"|||"
                self.socket.sendto(message, address)

                # se recibe el mensaje de confirmacion y se verifica este
                # finalmente se manda un mensaje de confirmacion devuelta
                message, destinity_address = self.socket.recvfrom(udp_buff_size)

                parsed_message = self.parse_segment(message.decode())
                parsed_headers = parsed_message["headers"]

                if parsed_headers["SYN"]:
                    if parsed_headers["ACK"]:
                        if parsed_headers["seq"] == self.sequence + 1:
                            message = "0|||1|||0|||" + str(self.sequence + 2) + "|||"
                            self.sequence += 2
                            self.destinity_address = destinity_address
                            self.socket.sendto(message.encode(), address)
                            return
                        else:
                            continue
                    else:
                        continue    
            except socket.timeout:
                continue

    def accept(self):
        
        while True:
            # se recibe el mensaje de confirmacion
            message, client_address = self.socket.recvfrom(udp_buff_size)
            parsed_syn_message = self.parse_segment(message.decode())
            self.destinity_address = client_address

            new_socket = SocketTCP()
            new_udp_socket = new_socket.socket
            new_client_address = (client_address[0], int(client_address[1]) + 1)
            new_socket.bind(new_client_address)
            new_socket.destinity_address = client_address
            

            # se verifica que el mensaje sea uno de sincronizacion
            if parsed_syn_message["headers"]["SYN"] == 1:
                parsed_syn_message["headers"]["ACK"] = 1
                self.sequence = parsed_syn_message["headers"]["seq"] + 1
                parsed_syn_message["headers"]["seq"] += 1
                send_message = self.create_segment(parsed_syn_message)
                new_udp_socket.sendto(send_message.encode(), client_address)

            # se recibe un mensaje de confirmacion, se verifica su contenido y se retorna el SocketTCP creado
            while True:
                try:
                    self.socket.settimeout(8)
                    ack_message, _ = self.socket.recvfrom(20)

                    parsed_ack_message = self.parse_segment(ack_message.decode())
                    parsed_ack_header = parsed_ack_message["headers"]

                    if parsed_ack_header["ACK"]:
                        if parsed_ack_header["seq"] == self.sequence + 1:
                            self.sequence += 1
                            new_socket.sequence = self.sequence
                            self.destinity_address = client_address
                            self.socket.settimeout(0)
                            return (new_socket,  self.destinity_address)
                        
                    else:
                        continue

                except socket.timeout:
                    break

    def send(self, message, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            self.send_using_stop_and_wait(message)
        elif mode == "go_back_n":
            self.send_using_go_back_n(message)

    def recv(self, buff_size, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            return self.recv_using_stop_and_wait(buff_size)
        elif mode == "go_back_n":
            return self.recv_using_go_back_n(buff_size)
    def close(self):
        # creacion mensaje de cierrte
        close_message = b"0|||0|||1|||" + (str(self.sequence)).encode() + b"|||"

        tries = 3

        while tries > 0:
            try:
                # creacion de timeout
                self.socket.settimeout(5)

                # envio mensaje de cierre
                self.socket.sendto(close_message, self.destinity_address)

                # se recibe mensaje de confirmacion de cierre
                close_confirmation_message, addesss = self.socket.recvfrom(udp_buff_size)
                parsed_close_confirmation_message = self.parse_segment(close_confirmation_message.decode())

                # se chequea si este mensaje es el correcot
                if parsed_close_confirmation_message["headers"]["FIN"] == 1:
                    if parsed_close_confirmation_message["headers"]["ACK"] == 1:
                        if parsed_close_confirmation_message["headers"]["seq"] == self.sequence + 1:
                            self.sequence += 2
                            confirmation_message = b"0|||0|||1|||" + (str(self.sequence)).encode() + b"|||"
                            internal_tries = 3

                            while internal_tries > 0:
                                try:
                                    self.socket.settimeout(5)
                                    self.socket.sendto(confirmation_message, addesss)
                                    internal_tries -= 1

                                except socket.timeout:
                                    internal_tries -= 1
                                    continue
                            break
                            

            except socket.timeout:
                tries -= 1
                continue

        self.socket.close()

    def recv_close(self):
        tries = 3

        while tries > 0:
            try:
                self.socket.settimeout(5)
                # se recibe el mensaje de cierre
                close_confirmation_message, address = self.socket.recvfrom(udp_buff_size)
                parsed_close_confirmation_message = self.parse_segment(close_confirmation_message.decode())

                # se verifica si corresponde a un mensaje de cierre y 
                # si lo es se manda el mensaje de confirmacion y se cierra el socket
                if parsed_close_confirmation_message["headers"]["FIN"] == 1:
                    parsed_close_confirmation_message["headers"]["ACK"] = 1
                    parsed_close_confirmation_message["headers"]["seq"] += 1
                    
                    send_confirmation_message = self.create_segment(parsed_close_confirmation_message)
                    self.sequence += 1
                    
                    self.socket.sendto(send_confirmation_message.encode(), address)
                    tries -= 1
                    # se recibe el mensaje de cierre
                    close_confirmation_message, address = self.socket.recvfrom(udp_buff_size)
                    parsed_close_confirmation_message = self.parse_segment(close_confirmation_message.decode())

                    if parsed_close_confirmation_message["headers"]["seq"] == self.sequence + 1:
                        self.sequence += 1
                        break
                else:
                        self.sequence += len(parsed_close_confirmation_message["body"])
                        confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                        self.socket.sendto(confirmation_message, address)
            
            except socket.timeout:
                tries -= 1
                continue

        self.socket.close()
            
        
    def send_using_stop_and_wait(self, message):
        # primer mensaje que se envia corresponde al largo del mensaje
        message_length = len(message)

        message_length_to_send = b"0|||0|||0|||" + (str(self.sequence)).encode() + b"|||" + (str(message_length)).encode()

        while True:
            try:
                self.socket.settimeout(5)
                self.socket.sendto(message_length_to_send, self.destinity_address)
                
                confirmation_message, _ = self.socket.recvfrom(udp_buff_size)
                parsed_confirmation_message = self.parse_segment(confirmation_message.decode())

                if ((parsed_confirmation_message["headers"]["ACK"] == 1) and (parsed_confirmation_message["headers"]["seq"] >= self.sequence + len(str(message_length)))):
                    self.sequence += len(str(message_length))
                    break

            except socket.timeout:
                continue

        # byte_inicial indica desde donde comenzamos a mandar el mensaje
        byte_inicial = 0

        # en message_sent_so_far vamos a guardar el mensaje completo que se ha enviado hasta el momento
        message_sent_so_far = ''.encode()

        # dentro del ciclo cortamos el mensaje en trozos de tamaño 16
        while True:
            try:
                self.socket.settimeout(5)
                
                # max_byte indica "hasta que byte" vamos a enviar, lo seteamos para evitar tratar de mandar más de lo que es posible
                max_byte = min(len(message), byte_inicial + 16)

                # obtenemos el trozo de mensaje
                message_slice = message[byte_inicial: max_byte]

                # Se decodifica el mensaje para agregarle el head tcp y despues de codifica devuelta
                message_tcp = b"0|||0|||0|||" + (str(self.sequence)).encode() + b"|||" + message_slice

                # mandamos el mensaje
                self.socket.sendto(message_tcp, self.destinity_address)

                # se recibe el mensaje
                recieved_message, _ = self.socket.recvfrom(udp_buff_size)
                parsed_recieved_message = self.parse_segment(recieved_message.decode())

                
                # se verifica que el mensaje corresponde al correcto
                if parsed_recieved_message["headers"]["ACK"] == 1:
                    if parsed_recieved_message["headers"]["seq"] >= self.sequence + (max_byte - byte_inicial):
                        # actualizamos cuánto hemos mandado
                        message_sent_so_far += message_slice
                        self.sequence += len(message_slice)

                        # si se manda y se recibe todo el mensaje se termina el mensaje
                        if (message_sent_so_far == message):
                            
                            break

                        # de lo contrario actualizamos el byte inicial para enviar el siguiente trozo
                        byte_inicial += 16

                        if (byte_inicial > len(message)):
                            byte_inicial -= (byte_inicial-len(message))
            
            except socket.timeout:
                continue

    def recv_using_stop_and_wait(self, buff_size):
        messages = ""
        # primer mensaje que recibe corresponde al largo del mensaje
        if self.rest == 0:
            while True:
                try:
                    self.socket.settimeout(15)

                    if self.message_length == self.rest:
                        break

                    recieved_message_length, address = self.socket.recvfrom(udp_buff_size)
                    parsed_message_length = self.parse_segment(recieved_message_length.decode())
                    
                    try:
                        self.message_length = int(parsed_message_length["body"])
                    except ValueError:
                        confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                        self.socket.sendto(confirmation_message, self.destinity_address)
                        continue
                    
                    self.sequence += 2 
                    self.rest = self.message_length

                    confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                    self.socket.sendto(confirmation_message, self.destinity_address)

                except socket.timeout:
                    continue

        # corresponde al caso en donde ya se recibio el largo del mensaje y se sabe cuanto deberia recibir 
        # caso donde todo el mensaje cabe en el buff_size
        if self.message_length <= buff_size:
            while True:
                try:
                    while self.rest > 0:
                        try:
                            self.socket.settimeout(4)
                            message, address = self.socket.recvfrom(udp_buff_size)
                            parsed_message = self.parse_segment(message.decode())

                            if parsed_message["headers"]["seq"] == self.sequence - 2:
                                confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                                self.socket.sendto(confirmation_message, self.destinity_address)
                                continue

                            self.sequence += len(parsed_message["body"])
                            messages += parsed_message["body"]
                            confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                            self.rest -= len(parsed_message["body"])
                            self.socket.sendto(confirmation_message, self.destinity_address)
                        except socket.timeout:
                            continue
                    return messages.encode()
                
                except socket.timeout:
                    continue
        
        # caso donde todo el mensaje no cabe en el buff_size
        else:
            while True:
                try:
                    # si el mensaje se corta porque el buff_size es muy chico entonces se tiene que llamar mas veces recv
                    """ if buff_size < 16: """
                    message, address = self.socket.recvfrom(udp_buff_size)
                    parsed_message = self.parse_segment(message.decode())

                    if parsed_message["headers"]["seq"] == self.sequence - 2:
                        confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                        self.socket.sendto(confirmation_message, self.destinity_address)
                        continue

                    # segunda llamada que se hace, se recibe mensaje directamente desde el body
                    if self.rest < self.message_length:
                        # caso en que ya se tiene guardado los valores
                        if self.cache != "":
                            temp = self.cache + parsed_message["body"]
                            self.cache = temp[buff_size:]
                            self.sequence += len(parsed_message["body"])
                            confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                            self.socket.sendto(confirmation_message, self.destinity_address)
                            return temp[0:buff_size].encode()
                            
                    # primera llamada que se hace
                    else:
                        self.cache = parsed_message["body"][buff_size:]
                        self.sequence += len(parsed_message["body"])
                        messages = parsed_message["body"][0:buff_size]
                        self.rest -= len(messages)
                        confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                        self.socket.sendto(confirmation_message, self.destinity_address)
                        return messages.encode()
                    
                except socket.timeout:
                    continue
            
    def send_using_go_back_n(self, message):

        message_length = len(message)

        MSS = 8
        congestion_controller = CongestionControl(MSS)

        data_list = []
        for i in range(0, len(message), MSS):
            data_list.append(message[i:i + MSS])

        full_message = [message_length] + data_list

        window_size = 3
        if len(full_message) < window_size:
            window_size = len(full_message)

        if MSS < window_size:
            window_size = MSS

        window = swcc.SlidingWindowCC(window_size, full_message, self.sequence, False)
        window_index = 0

        timer_list = tl.TimerList(5, len(full_message)) 
        timer_index = 0

        while True:
            try:
                # envio de todos los mensajes en la ventana
                # esto incluye el primer segmento y los segmentos posteriores
                if self.finished == False:
                    while window_index < window_size:

                        current_segment = window.get_data(window_index)
                        
                        if current_segment == None:
                            self.finished = True
                            break

                        current_sequence = window.get_sequence_number(window_index)

                        tcp_message = b"0|||0|||0|||" + (str(current_sequence)).encode() + b"|||" + current_segment
                        self.socket.sendto(tcp_message, self.destinity_address)

                        # se crea el tiemer para el envio del primer segmento
                        if window_index == 0:
                            timer_list.start_timer(window_index)

                        self.sequence += len(current_segment)
                        
                        window_index += 1

                window_index = 0
                while window_index < window_size:

                    confirmation_message, _ = self.socket.recvfrom(udp_buff_size)
                    # si es el primer segmento enviado se para el timeout
                    if window_index == 0:
                            timer_list.stop_timer(window_index)

                    # while True:
                    # se parsea el segmento y se obtiene el segmento esperado
                    parsed_confirmation_message = self.parse_segment(confirmation_message.decode())
                    
                    # if window
                    current_segment = window.get_data(window_index)
                    expected_window_seq = window.get_sequence_number(window_index)
                    

                    # si corresponde mensaje indicado se recibe y se manda un nuevo mensaje
                    if parsed_confirmation_message["headers"]["ACK"] == 1:
                        if parsed_confirmation_message["headers"]["seq"] >= expected_window_seq + len(current_segment):
                            
                            self.socket.settimeout(5)

                            window.move_window(1)

                            congestion_controller.event_ack_received()
                            new_window_size = congestion_controller.get_cwnd()
                            window.update_window_size(new_window_size)

                            if parsed_confirmation_message["headers"]["seq"]  == self.sequence:
                                self.finished = False
                                return


                            if window_size < new_window_size:
                                window_index = new_window_size - window_size - window_index

                            window_index = 2

                            window_size = congestion_controller.get_cwnd()

                            break
                                
                        window_index += 1

            except socket.timeout:
                congestion_controller.event_timeout()
                window.update_window_size(congestion_controller.get_cwnd())
                continue
            
    def recv_using_go_back_n(self, buff_size):

        messages = ""
        if self.rest == 0:
            # el primer mensaje corresponde al largo del mensaje
            recieved_message, _ = self.socket.recvfrom(udp_buff_size)
            parsed_recieved_message = self.parse_segment(recieved_message.decode())

            self.message_length = int(parsed_recieved_message["body"])
            self.rest = self.message_length
            self.sequence += len(parsed_recieved_message["body"])

            confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
            self.socket.sendto(confirmation_message, self.destinity_address)

        if self.message_length <= buff_size:

            while self.rest > 0:
                # el segundo mensaje en adeltante corresponde al mensaje en si
                recieved_message, _ = self.socket.recvfrom(udp_buff_size)
                parsed_recieved_message = self.parse_segment(recieved_message.decode())
                
            
                if parsed_recieved_message["headers"]["seq"] > self.sequence:
                    continue

                if parsed_recieved_message["headers"]["seq"] == self.sequence:
                    self.sequence += len(parsed_recieved_message["body"])
                    self.rest -= len(parsed_recieved_message["body"])
                    messages += parsed_recieved_message["body"]

                    confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                    self.socket.sendto(confirmation_message, self.destinity_address)

                    if self.rest == 0:
                        return  messages.encode()
                
        else:
            messages = ""
            while True:
                # recibir un mensaje

                recieved_message, _ = self.socket.recvfrom(udp_buff_size)
                parsed_recieved_message = self.parse_segment(recieved_message.decode())

                if parsed_recieved_message["headers"]["seq"] > self.sequence:
                    continue

                # segunda llamada que se hace, se recibe mensaje directamente desde el body
                if self.rest < self.message_length:
                    # caso en que ya se tiene guardado los valores
                    if self.cache != "":
                        temp = self.cache + parsed_recieved_message["body"]
                        self.cache = temp[buff_size:]
                        self.sequence += len(parsed_recieved_message["body"])
                        self.rest -= len(parsed_recieved_message["body"])
                        
                        confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                        self.socket.sendto(confirmation_message, self.destinity_address)
                        
                        if len(temp) >= len(self.cache):
                            return temp[0:buff_size].encode()

                else:
                    self.rest -= len(parsed_recieved_message["body"])
                    self.sequence += len(parsed_recieved_message["body"])

                    if len(parsed_recieved_message["body"]) <= buff_size:
                        self.cache += parsed_recieved_message["body"]

                        confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                        self.socket.sendto(confirmation_message, self.destinity_address)
                        continue

                    self.cache = parsed_recieved_message["body"][buff_size:]
                    messages = parsed_recieved_message["body"][0:buff_size]

                    confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                    self.socket.sendto(confirmation_message, self.destinity_address)
                    return messages.encode()
                