import SocketTCP
import sys

direction = sys.argv[1]
port = sys.argv[2]

address = (direction, int(port))

# CLIENT
client_socketTCP = SocketTCP.SocketTCP()
client_socketTCP.connect(address)

client_socketTCP.close()