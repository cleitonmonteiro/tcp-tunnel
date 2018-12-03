from sys import argv
from models_servidor import HandleConnection

try:
    port     = int( argv[1] )
    file_dir = argv[2]
except:
    print('d Usage : {} <port> <file_dir>'.format( argv[0] ))
    exit(-1)

clients = []

hc = HandleConnection( port, file_dir, clients)

print('d Starting HandleConnection...')
print('d Use Ctrl+C to stop server.')
hc.start()
