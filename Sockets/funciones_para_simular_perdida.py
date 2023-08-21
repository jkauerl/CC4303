import random


def recv_con_perdidas(socket, buff_size, loss_probability):
    while True:
        # recibimos el mensaje
        buffer = socket.recv(buff_size)
        # sacamos un número entre 0 y 100 de forma aleatoria
        random_number = random.randint(0, 100)
        # si el random_number es menor o igual a la probabilidad de perdida omitimos el mensaje
        if random_number <= loss_probability:
            continue
        # de lo contrario salimos del loop y retornamos
        else:
            break
    return buffer


def send_con_perdidas(socket, message_in_bytes, loss_probability):
    # sacamos un número entre 0 y 100 de forma aleatoria
    random_number = random.randint(0, 100)
    # si el random_number es mayor o igual a la probabilidad de perdida enviamos el mensaje
    if random_number >= loss_probability:
        socket.send(message_in_bytes)

