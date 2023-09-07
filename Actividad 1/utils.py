import json
import re

# definimos el path donde se encuentra el archivo que queremos enviar
path = f"Actividad 1/actividad1.html"
file = open(path, "r")
response_body = file.read()
response_head = """HTTP/1.1 200 OK
Server: nginx/1.17.0
Date: Thu, 24 Aug 2023 15:54:05 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 145
Connection: keep-alive
Access-Control-Allow-Origin: *
"""
response_head += "X-ElQuePregunta: "

forbidden_message = """HTTP/1.1 403 Forbidden
Content-Type: text/html
Content-Length: 146

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>CC4303</title>
</head>
<body>
    <h1>Forbidden</h1>
</body>
</html>"""

# Funcion que decodifica y guarda el mensaje en una lista [head, body]
def parse_HTTP_message(http_message):
    http_message = http_message.decode()
    decoded_http_message = http_message.split("\r\n\r\n", 1)

    head = decoded_http_message[0]
    body = decoded_http_message[1]

    headers = head.split("\r\n")
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

 
def check_blocked_sites(first_line, location_json, name_json):
    with open((location_json + "/" + name_json + ".json")) as file:
        # usamos json para manejar los datos
        data = json.load(file)

        pattern = r'GET (https?://[^\s]+) HTTP/1.1'
        requested_site = re.search(pattern, first_line)

        for i in data["blocked"]:
            if i == requested_site.group(1):
                return 1
        else:
            return 0

def replace_forbidden_words(http_message, location_json, name_json):
    with open((location_json + "/" + name_json + ".json")) as file:
        # usamos json para manejar los datos
        data = json.load(file)
        forbidden_words = data["forbidden_words"]
        new_body = http_message[1]

        # remplazar las palabras prohibidas
        for i in forbidden_words:
            for key, value in i.items():
                new_body = new_body.replace(key, value)

        # actualizar el tamaño de content-length
        new_bytes_size = len(new_body.encode('utf-8'))
        http_message[0]["Content-Length"] = str(new_bytes_size)

        return [http_message[0], new_body]