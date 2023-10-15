import SocketTCP

# client
address = ('localhost', 5000)

client_socketTCP = SocketTCP.SocketTCP()
client_socketTCP.connect(address)
