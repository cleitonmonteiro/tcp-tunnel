from sys import argv
from models import HandleConnection


try:
    port     = int( argv[1] )
    file_dir = argv[2]
except:
    print('d Usage : {} <port> <file_dir>'.format( argv[0] ))

clients = []

hc = HandleConnection( port, file_dir, clients)
hc.start()

