# Informe Actividad 3: Construir un Proxy
# CC4303: Redes

Profesora: Ivana Bachmann
Auxiliar: Vicente Videla
Estudiante: Javier Kauer
Fecha de entrega: 21/10/2023

## Desarrollo

Para esta actividad se siguieron los pasos tal cual descrito en la sección de la actividad. 

Además se utilizaron las siguiente librerías. Sockets, random, y las clases SlidingWindo, TimerList, SocketTCP programada en la actividad anterior, y la clase SocketUDP para simular perdidas a mano.


### Parte 1

En esta parte se tiene que programar un simulador de control de congestión programando la clase CongestionControl. Esta clase simula el control de congestión propio de la famosa implementación de TCP Tahoe. Por lo tanto solamente tiene 2 estados, los cuales corresponden a slow start, y a congestion avoidance.

A continuación se presenta el código de la clase entera:

``` python
class CongestionControl():

    def __init__(self, mss):
        self.mss = mss
        self.current_state = "slow start"
        self.cwnd = mss # esta valor esta en bytes
        self.ssthresh = None
        self.fraction = 0

    def get_cwnd(self):
        """ retorna el valor de cwnd almacenado en la clase
        """
        return self.cwnd
    
    def get_MSS_in_cwnd(self):
        return self.get_cwnd() // self.mss 
        
    def get_ssthresh(self):
        return self.ssthresh
        
    def is_state_slow_start(self):
        if self.current_state == "slow start":
            return True
        else:
            return False
        
    def is_state_congestion_avoidance(self):
        if self.current_state == "congestion avoidance":
            return True
        else:
            return False
        
    def event_ack_received(self):

        if self.is_state_slow_start():
            self.cwnd += self.mss
            if self.ssthresh != None:
                if self.cwnd >= self.ssthresh:
                    self.current_state = "congestion avoidance"
                    self.ssthresh = self.get_cwnd() / 2
        
        elif self.is_state_congestion_avoidance():
            self.cwnd += 1 // self.get_MSS_in_cwnd() * self.mss
            self.fraction = 1 / self.get_MSS_in_cwnd() * self.mss - 1 // self.get_MSS_in_cwnd() * self.mss
            if (self.fraction // 1).is_integer():
                self.cwnd += self.fraction
                
    def event_timeout(self):

        if self.is_state_slow_start():
            self.ssthresh = self.get_cwnd() / 2
            self.cwnd = self.mss
        elif self.is_state_congestion_avoidance():
            self.current_state = "slow start"
            self.cwnd = self.mss 
            self.ssthresh += (self.get_cwnd() // 2) * self.get_MSS_in_cwnd()
```

Tal como se puede observar, esta implementación tiene los siguiente atributos: MSS, cwnd, ssthresh y el estado actual. Además se tiene los gettters relevantes, los cuales son para sshthres, cwn y la cantidad de veces que MSS cabe en ssthresh. Además cuenta con los métodos para saber en que estado actual se encuentra la clase. Finalmente, todos los métodos comentados anteriormente sirven para crear los siguientes 2 métodos: event_ack_recieved, y event_timeout. Los cuales sirven para manejar las condiciones cuando se recibe un ACK, y como cambiar los valores, y qué cambios suceden cuando se ocurre un timeout en cada estado, respectivamente.


### Parte 2

Preguntas:

1. La razón por la cual sirve usar como base el código de Stop & Wait para implementar Go Back N, es porque de cierta forma este último presenta un comportamiento generalizado (pero limitado) de Stop & Wait. Esto sucede porque se puede pensar que Stop & Wait tiene una ventana de largo 1, en donde espera que se envie y se confirme el envió de solamente 1 segmento, también se hacen esperas de confirmación de paquete para continuar enviando, y recibiendo, segmentos nuevos.

2. Esta función no debería cambiar mucho comparado con Stop & Wait, esto porque recieve de Go Back N cumple el mismo funcionamiento del primero. La razón de esto porque este método solamente toma los valores recibidos por el emisor, aumenta el numero de secuencia, y manda un mensaje de confirmación al emisor. Esto sucede porque tal cual como funciona Go Back N, este solamente manda ACK, si el segmento previo llegó, y mandó un ACK. Además no debería cambiar con respecto a las nuevas clases otorgadas porque estas clases se ocupan por parte del emisor. En donde el emisor se encarga de enviar los segmentos dentro de la venta, y manejar los timeouts de ellos.

Es importante comentar el manejo de pérdidas que se debería hacer en recieve. Esto puesto porque si un segmento no llega, entonces se sigue esperando hasta que llegue, y si llega y se pierde el ack, entonces solamente tiene que esperar a que llegue el próximo segmento. De esta forma Go Back N no es relativamente simple.

En esta parte, se implementa los métodos de send_using_go_back_n, y recv_using_go_back_n. También se implementa la opción de poder elegir que mécanismo usar para enviar, y recibir código. Finalmente, se simula péridas a mano usando la clase de SocketUDP.

El código de esto se encuentra a continuación, en la clase de SocketTCP2:

``` python
def send_using_go_back_n(self, message):

    message_length = len(message)

    split_message = []
    for i in range(0, len(message), 16):
        split_message.append(message[i:i + 16])

    full_message = [message_length] + split_message


    window_size = 3
    if len(full_message) < window_size:
        window_size = len(full_message)

    window = swcc.SlidingWindowCC(window_size, full_message, self.sequence)
    window_index = 0


    timer_list = tl.TimerList(5, len(full_message)) 
    timer_index = 0

    while True:
        try:
            # envio de todos los mensajes en la ventana
            # esto incluye el primer segmento y los segmentos posteriores
            while window_index < window_size:

                current_segment = window.get_data(window_index)
                current_sequence = window.get_sequence_number(window_index)

                tcp_message = b"0|||0|||0|||" + (str(current_sequence)).encode() + b"|||" + current_segment
                self.socket.sendto(tcp_message, self.destinity_address)

                # se crea el tiemer para el envio del primer segmento
                if window_index == 0:
                    timer_list.start_timer(window_index)
                    # ojo con el comentario de abajo
                    # self.socket.setblocking(False)

                self.sequence += len(current_segment)
                
                window_index += 1
                    

            window_index = 0
            while window_index < window_size:
                confirmation_message, _ = self.socket.recvfrom(udp_buff_size)
                # si es el primer segmento enviado se para el timeout
                if window_index == 0:
                        timer_list.stop_timer(window_index)

                while True:
                    # se parsea el segmento y se obtiene el segmento esperado
                    parsed_confirmation_message = self.parse_segment(confirmation_message.decode())
                    
                    # if window
                    expected_window_seq = window.get_sequence_number(1)
                    
                    if expected_window_seq == None:
                                return
                    # si corresponde mensaje indicado se recibe y se manda un nuevo mensaje
                    if parsed_confirmation_message["headers"]["ACK"] == 1:
                        if parsed_confirmation_message["headers"]["seq"] >= expected_window_seq or parsed_confirmation_message["headers"]["seq"] == self.sequence:
                            
                            window.move_window(1)
                            
                    window_index += 1
                    break

        except BlockingIOError:
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
                    self.cache = parsed_recieved_message["body"]

                    confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                    self.socket.sendto(confirmation_message, self.destinity_address)
                    continue

                self.cache = parsed_recieved_message["body"][buff_size:]
                messages = parsed_recieved_message["body"][0:buff_size]

                confirmation_message = b"0|||1|||0|||" + (str(self.sequence)).encode() + b"|||"
                self.socket.sendto(confirmation_message, self.destinity_address)
                return messages.encode()

```

### Parte 3

Finalmente, se agrega la clase de CongestionControl en la funcionalidad de enviar mensaje usando Go Back N.

Es decir, se coloca los métodos programados en el paso 1, en las ubicaciones correctas. Es decir, cuando el emisor recibe un mensaje de confirmación (ACK), se agrega el método event_ack_recieved(), y cuando sucede un timeout, se incluye el método event_timeout(). 

También se agrega la funcionalidad de cambiar el tamaño de la ventana, para lograr usar esto, se decide usar el atributo de cwnd para variar el tamaño de la ventana. También en vez de dividir el mensaje en tamaño de 16 bytes, se divide en segmentos de tamaño 8. Finalmente, se maneja el caso cuando se tiene que enviar más segmentos al momento de modificar, y cambiar el tamaño de la ventana.

El código se encuentra en la clase SocketTCP3, el cual se muestra el método actualizado de send_using_go_back_n():

``` python
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
```

## Resultados Obtenidos

Para ejecutar los tests, se va variando la clase importada en los archivos de cliente5, cliente6, servidor 5, y cliente6.

Para probar que la clase de CongestionControler funciona, se ocupa el archivo CongestionController_test, y se corre el test. Se observa que se cumplen los tests, y también cuando se varía el valor de MSS.

Para el test de uso de congestion controller, se observa que se llegan los mensajes correctamente. Este se hace usando la clase de SocketUDP.

La implementación de congestion controller se comporta correctamente. Se observa que no ocurren timeouts de forma espontánea, y no se cambian los atributos de estado actual, y los parámetros de la clase.

Es más robusto ocupar control de congestion porque hace que la red sea fair.