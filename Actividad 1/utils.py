""" #  Estructura para almacenar el body y el head de un mensaje http
class HTTP_Message():

    def __init__(self, head, body):
        self.head = head
        self.body = body """

# Funcion que decodifica y guarda el mensaje en una lista [head, body]
def parse_HTTP_message(http_message):
    decoded_http_message = decoded_http_message.decode()
    decoded_http_message = http_message.split('\r\n\r\n')

    parse_HTTP = [decoded_http_message[0] + '\r\n\r\n', decoded_http_message[1]]

    return  parse_HTTP

# Funcion que recibe la lista [head, body] y retorna un mensaje codificado
def create_HTTP_message(parse_HTTP):
    http_message = parse_HTTP[0] + parse_HTTP[1]
    return http_message.encode()

 
