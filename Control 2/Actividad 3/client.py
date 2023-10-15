import socket


# creamos el socket cliente (no orientado a conexión)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 5000)

message = ""
while True:
    try:
        message += input() + '\n'
    except EOFError:
        break

# byte_inicial indica desde donde comenzamos a mandar el mensaje
byte_inicial = 0

message = message.encode()

# en message_sent_so_far vamos a guardar el mensaje completo que se ha enviado hasta el momento
message_sent_so_far = ''.encode()

# dentro del ciclo cortamos el mensaje en trozos de tamaño 16
while True:
    # max_byte indica "hasta que byte" vamos a enviar, lo seteamos para evitar tratar de mandar más de lo que es posible
    max_byte = min(len(message), byte_inicial + 16)

    # obtenemos el trozo de mensaje
    message_slice = message[byte_inicial: max_byte]

    # Se decodifica el mensaje para agregarle el head tcp y despues de codifica devuelta
    message_tcp = b"0|||0|||0|||" + message_slice

    # mandamos el mensaje
    client_socket.sendto(message_tcp, server_address)

    # actualizamos cuánto hemos mandado
    message_sent_so_far += message_slice

    if (message_sent_so_far == message):
        break

    # de lo contrario actualizamos el byte inicial para enviar el siguiente trozo
    byte_inicial += 16

    if (byte_inicial > len(message)):
        byte_inicial -= (byte_inicial-len(message))
    






