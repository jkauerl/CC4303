import SocketTCP

address = ('localhost', 5000)

# SERVER
server_socketTCP = SocketTCP.SocketTCP()
server_socketTCP.bind(address)
connection_socketTCP, new_address = server_socketTCP.accept()

connection_socketTCP.recv_close()