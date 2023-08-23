""" #  Estructura para almacenar el body y el head de un mensaje http
class HTTP_Message():

    def __init__(self, head, body):
        self.head = head
        self.body = body """

# Funcion que decodifica y guarda el mensaje en una lista [head, body]
def parse_HTTP_message(http_message):
    print(http_message)
    http_message = http_message.decode()
    decoded_http_message = http_message.split("\r\n\r\n", 1)

    head = decoded_http_message[0]
    body = decoded_http_message[1]

    headers = head.split("\r\n", 1)
    headers_dict = {}
    for i in range(len(headers)):
        if i == 0:
            headers_dict["first_line"] = headers[i]
        else:
            header = headers[i].split(": ", 1)
            headers_dict[header[0]] = header[1]
            
    parse_HTTP = [ headers_dict, body]

    return  parse_HTTP

# Funcion que recibe la lista [head, body] y retorna un mensaje codificado
def create_HTTP_message(parse_HTTP):   
    headers_dict = parse_HTTP[0] 
    body = parse_HTTP[1]
    
    headers = ""
    for key in headers_dict.keys():
        if key == "first_line":
            headers += headers_dict[key] + "\r\n"
        else:
            headers += key + ": " + headers_dict[key] + "\r\n"
    
    http_message = headers + "\r\n" + body

    return http_message.encode()

 
