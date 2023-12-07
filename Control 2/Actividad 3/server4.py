import SocketTCP

# server 
address = ('localhost', 5000)

server_socketTCP = SocketTCP.SocketTCP()
server_socketTCP.bind(address)
connection_socketTCP, new_address = server_socketTCP.accept()