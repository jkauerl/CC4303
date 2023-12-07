import socket
import random
import datetime

debug_mode = True

def debug_print(*args, **kwargs):
    """ Esta funcion se encarga de imprimir mensajes de debug en caso de que
    debug_mode sea True
    
    Es solamente un print envuelto en un if, sirve para poder
    desactivar/activar el debugging facilmente
    """
    if debug_mode:
        print(*args, **kwargs)

class SocketUDP():
    """ Wrapper un socket UDP para simular perdidas
    
    Para simular lo que hace netem (solo perdidas, no el delay), hay que setear
    los atributos send_loss_rate y recv_loss_rate en 0.2 y usar este socket en
    lugar de uno normal (son los mismos metodos)
    """
    def __init__(self):
        # El unico campo de esta clase es el socket que se va a usar
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_loss_rate = None
        self.recv_loss_rate = None

    def sendto(self, data, addr, loose=False, send_loss_rate=None):
        """ Esta funcion se encarga de mandar paquetes a traves del socket
        Simula perdidas obteniendo un numero aleatorio entre 0 y 1 y
        comparandolo con send_loss_rate
        
        Argumentos:
            - `data (bytes)`: bytes a enviar
            - `addr (tuple)`: tupla con la direccion y el puerto del 
                destinatario
            - `loose (bool)`: si es True, se fuerza la perdida del paquete
            - `send_loss_rate (float)`: probabilidad de perdida del
                paquete (valor entre 0 y 1)

        Por defecto loose es falso para que la perdida se calcule segun la
        probabilidad, pero puede setearse a True para forzar la perdida de
        algun paquete en particular por motivos de debugging (evocar casos
        borde).

        Si no se especifca un send_loss_rate en la invocacion de la 
        funcion, se intentara usar el send_loss_rate interno del socket.
        Si ninguno esta seteado (los dos son `None`), se probara con una
        probabilidad de perdida de 0.0
        """
        now = datetime.datetime.now().strftime("%M:%S")

        # Se calcula la probabilidad de perdida
        if send_loss_rate is None:
            send_loss_rate = self.send_loss_rate
        if send_loss_rate is None:
            send_loss_rate = 0.0
        
        if loose or random.random() < send_loss_rate:
            # En caso de que se pierda el paquete se informa con este mensaje
            # Y no se manda
            debug_print(f"        <XXX [{now} - SENDTO] XXX> Lost package: {data}")
        else:
            # En caso de que se bypasee la probabilidad de perdida, se informa y se manda
            debug_print(f"    <--- [{now} - SENDTO] ---> Sent package: {data}")
            self.sock.sendto(data, addr)

    def recvfrom(self, buff_size, loose=False, recv_loss_rate=None) -> bytes:
        """ Esta funcion se encarga de recibir paquetes a traves del socket
        Simula perdidas obteniendo un numero aleatorio entre 0 y 1 y
        comparandolo con recv_loss_rate

        Botara paquetes hasta que reciba uno que no se pierda, y ese 
        sera el que retorne finalmente.

        Argumentos:
            - `buff_size (int)`: tamaño del buffer a recibir
            - `loose (bool)`: si es True, se fuerza la perdida del paquete
            - `recv_loss_rate (float)`: probabilidad de perdida del paquete
                (valor entre 0 y 1)

        Por defecto loose es falso para que la perdida se calcule segun la
        probabilidad, pero puede setearse a True para forzar la perdida de
        algun paquete en particular por motivos de debugging (evocar casos
        borde). loose se setea automaticamente a True despues de perder
        un paquete para evitar que se pierdan todos los paquetes.

        Si no se especifca un recv_loss_rate en la invocacion de la
        funcion, se intentara usar el recv_loss_rate interno del socket.
        Si ninguno esta seteado (los dos son `None`), se probara con una
        probabilidad de perdida de 0.0
        """
        
        while True:
            # Se intenta recibir un paquete
            now = datetime.datetime.now().strftime("%M:%S")
            buffer, address = self.sock.recvfrom(buff_size)

            # Se calcula la probabilidad de perdida
            if recv_loss_rate is None:
                recv_loss_rate = self.recv_loss_rate
            if recv_loss_rate is None:
                recv_loss_rate = 0.0
            
            if loose or random.random() < recv_loss_rate:
                # En caso de que se pierda el paquete se informa con este
                # mensaje y se vuelve a intentar recibir
                debug_print(f"        <XXX [{now} - RECVFR] XXX> Lost package: {buffer}")
                # Seteo lose a False para que no se pierdan todos los paquetes
                loose = False
            else:
                # En caso de que se bypasee la probabilidad de perdida, se
                # informa y se retorna
                debug_print(f"    <--- [{now} - RECVFR] ---> Received package: {buffer}")
                return buffer, address

    def bind(self, address):
        """ Override de bind """
        self.sock.bind(address)

    def settimeout(self, timeout):
        """ Override de settimeout """
        self.sock.settimeout(timeout)

    def close(self):
        """ Override de close """
        self.sock.close()

def reset_sockets(sock, recv, sender_address, receiver_address):
    """ Esta funcion se encarga de resetear los sockets a su estado inicial
    Solo la uso para el ejemplo de uso y es para evitar que quede basura """
    
    sock.close()
    recv.close()

    sock = SocketUDP()
    recv = SocketUDP()
    
    sock.bind(sender_address)
    recv.bind(receiver_address)

    recv.settimeout(1)

    return sock, recv

if __name__ == "__main__":
    # Ejemplo de uso:
    # Se recomienda dejar debug_mode en True para ver que ocurre
    # Se crean los sockets
    sender_address = ("localhost", 8080)
    receiver_address = ("localhost", 8081)

    sock = SocketUDP()
    sock.bind(sender_address)
    
    recv = SocketUDP()
    recv.bind(receiver_address)

    # Se envia y recibe sin perdidas
    print("Enviando y recibiendo sin perdidas")
    sock.sendto(b"Hello world!", receiver_address)
    try:
        data_received, _ = recv.recvfrom(1024)
    except socket.timeout:
        print("Se perdieron todos los paquetes!")
    else:
        print(f"Sent:     Hello world!")
        print(f"Received: {data_received.decode()}")
    print()

    sock, recv = reset_sockets(sock, recv, sender_address, receiver_address)

    # Se envian dos paquetes y se pierde uno (forzado con loose)
    print("Forzando perdida de paquete con loose = True")
    sock.sendto(b"First message", receiver_address, loose=True)
    sock.sendto(b"Second message", receiver_address)
    try:
        data_received, _ = recv.recvfrom(1024)
    except socket.timeout:
        print("Se perdieron todos los paquetes!")
    else:
        print(f"Sent:     First message")
        print(f"Sent:     Second message")
        print(f"Received: {data_received.decode()}")
    print()

    sock, recv = reset_sockets(sock, recv, sender_address, receiver_address)

    # Se envian dos paquetes y se pierde uno (con send_loss_rate manual)
    # El resultado de esta seccion cambia por ejecucion
    print("Evocando perdida de paquete con send_loss_rate = 0.5 (manual)")
    sock.sendto(b"First message", receiver_address, send_loss_rate=0.5)
    sock.sendto(b"Second message", receiver_address, send_loss_rate=0.5)
    sock.sendto(b"Third message", receiver_address, send_loss_rate=0.5)
    try:
        data_received, _ = recv.recvfrom(1024)
    except socket.timeout:
        print("Se perdieron todos los paquetes!")
    else:
        print(f"Sent:     First message")
        print(f"Sent:     Second message")
        print(f"Sent:     Third message")
        print(f"Received: {data_received.decode()}")
    print()

    sock, recv = reset_sockets(sock, recv, sender_address, receiver_address)

    # Se envian dos paquetes y se pierde uno (con send_loss_rate interno)
    # Esta es la manera que simula netem
    print("Evocando perdida de paquete con send_loss_rate = 0.3 (interno)")
    sock.send_loss_rate = 0.3
    sock.sendto(b"First message", receiver_address)
    sock.sendto(b"Second message", receiver_address)
    sock.sendto(b"Third message", receiver_address)
    try:
        data_received, _ = recv.recvfrom(1024)
    except socket.timeout:
        print("Se perdieron todos los paquetes!")
    else:
        print(f"Sent:     First message")
        print(f"Sent:     Second message")
        print(f"Sent:     Third message")
        print(f"Received: {data_received.decode()}")
    print()

    sock, recv = reset_sockets(sock, recv, sender_address, receiver_address)

    # Se envian dos paquetes y se pierde uno (al recibir) (forzado con loose)
    # El resultado de esta seccion cambia por ejecucion
    print("Evocando perdida de paquete (al recibir) con loose = True")
    sock.sendto(b"First message", receiver_address)
    sock.sendto(b"Second message", receiver_address)
    try:
        data_received, _ = recv.recvfrom(1024, loose=True)
    except socket.timeout:
        print("Se perdieron todos los paquetes!")
    else:
        print(f"Sent:     First message")
        print(f"Sent:     Second message")
        print(f"Received: {data_received.decode()}")
    print()

    sock, recv = reset_sockets(sock, recv, sender_address, receiver_address)

    # Se envian dos paquetes y se pierde uno (al recibir) (con recv_loss_rate manual)
    print("Evocando perdida de paquete (al recibir) con recv_loss_rate = 0.3 (manual)")
    sock.sendto(b"First message", receiver_address)
    sock.sendto(b"Second message", receiver_address)
    try:
        data_received, _ = recv.recvfrom(1024, recv_loss_rate=0.3)
    except socket.timeout:
        print("Se perdieron todos los paquetes!")
    else:
        print(f"Sent:     First message")
        print(f"Sent:     Second message")
        print(f"Received: {data_received.decode()}")
    print()

    sock, recv = reset_sockets(sock, recv, sender_address, receiver_address)

    # Se envian dos paquetes y se pierde uno (al recibir) (con recv_loss_rate interno)
    # Esta es la manera que simula netem
    print("Evocando perdida de paquete (al recibir) con recv_loss_rate = 0.3 (interno)")
    recv.recv_loss_rate = 0.3
    sock.sendto(b"First message", receiver_address)
    sock.sendto(b"Second message", receiver_address)
    try:
        data_received, _ = recv.recvfrom(1024)
    except socket.timeout:
        print("Se perdieron todos los paquetes!")
    else:
        print(f"Sent:     First message")
        print(f"Sent:     Second message")
        print(f"Received: {data_received.decode()}")
    print()

    sock.close()
    recv.close()