""" test = b"1 2 3 \r\n\r\n a"

print(test)
print(test.decode())
print(test.decode().split("\r\n"))
 """

""" 
import os

print(os.getcwd()) """
from bs4 import BeautifulSoup

html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>¿Qué es un proxy?</title>
</head>
<body>
    <h2>¿Qué es un proxy?</h2>
    <p>Un proxy es cualquier dispositivo intermedio entre un cliente y servidor, comúnmente utilizado para realizar las consultas a nombre del cliente y luego reenviárselas. Un proxy necesita ser capaz de recibir consultas como lo haría un servidor y luego (re)enviarlas como lo haría un cliente. Un ejemplo de uso de proxy es acceder desde sus casas a artículos científicos usando el proxy del DCC. Artículos a los que ustedes no acceso, pero la Universidad sí. Esto funciona pues al utilizar el proxy del DCC para solicitar un artículo a una biblioteca a la cual la Universidad tiene acceso, el proxy del DCC reenvía su petición desde la red del DCC la cual es parte de la red de la Universidad. Luego desde la biblioteca ven que la Universidad está solicitando un artículo y como esta tiene acceso a la biblioteca, le entregan el artículo sin problemas. Finalmente el artículo es recibido por el proxy del DCC y quien reenvía el artículo a ustedes en sus casas.</p>
</body>
</html>
"""

# Parse the HTML content
soup = BeautifulSoup(html, 'html.parser')

# Find all the text in the HTML
text = soup.get_text()

# Print the extracted text
print(text)