""" #  Estructura para almacenar el body y el head de un mensaje http
class HTTP_Message():

    def __init__(self, head, body):
        self.head = head
        self.body = body """

# Funcion que decodifica y guarda el mensaje en una lista [head, body]
def parse_HTTP_message(http_message):
    # print("test")
    # print(http_message)
    http_message = http_message.decode()
    decoded_http_message = http_message.split("\r\n\r\n")

    head = decoded_http_message[0]
    body = decoded_http_message[1]

    headers = head.split("\r\n")
    print(head)
    print(headers)
    headers_dict = []
    for i in range(len(headers)):
        if i == 0:
            
    parse_HTTP = [ , ]


    return  parse_HTTP

# Funcion que recibe la lista [head, body] y retorna un mensaje codificado
def create_HTTP_message(parse_HTTP):
    http_message = parse_HTTP[0] + parse_HTTP[1]
    return http_message.encode()

 
