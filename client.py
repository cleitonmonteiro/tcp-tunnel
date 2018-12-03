from sys import argv
from models_cliente import ConnectionToServer


try:
    server_ip= argv[1]
    port     = int( argv[2] )
    filename = argv[3]
except:
    print('d Usage : {} <server_hostname_or_ip> <port> <filename>'.format( argv[0] ))
    exit(-1)

try:
    print('d Starting ConnectionToServer...')
    print('d Use Ctrl+C to stop all process.')
    connection = ConnectionToServer( (server_ip, port), filename )
    connection.connect_to_server()
    connection.send_file()
    connection.close()
except KeyboardInterrupt as ki:
    print('\nd Used Ctrl+C.')
    print('d Stopping all process.')
    connection.close()