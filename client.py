import socket
import ctypes
from cabecalho import Pacote

port = 5005
msg = Pacote()
msg.contruir_pacote(12345,0,0,2,"testando 123 testando,")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,)
sock.sendto(msg.para_rede(), ("", port))