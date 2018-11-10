from sys import argv
from models import ConnectionToServer

try:
    server_ip= int( argv[1] )
    port     = int( argv[2] )
    filename = argv[3]
except:
    print('d Usage : {} <server_hostname_or_ip> <port> <filename>'.format( argv[0] ))

connection = ConnectionToServer( (server_ip, port), filename )
connection.connect_to_server()
connection.send_file()
connection.close()
