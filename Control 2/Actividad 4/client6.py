import SocketTCP3
import sys

direction = sys.argv[1]
port = sys.argv[2]

address = (direction, int(port))

# CLIENT
client_socketTCP = SocketTCP3.SocketTCP()
client_socketTCP.connect(address)
""" # test 1
message = "Mensje de len=16".encode()
client_socketTCP.send(message, "go_back_n") """
# test 2
message = "Mensaje de largo 19".encode()
client_socketTCP.send(message, "go_back_n")
# test 3
message = "Mensaje de largo 19".encode()
client_socketTCP.send(message, "go_back_n")

client_socketTCP.close()