import socket
import sys
from cabecalho import Pacote

port     = int( sys.argv[1] )
arquivo  = sys.argv[2]

class Cliente():

    def __init__( self, port, arquivo ):
        self.sock     = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )    
        self.port     = port
        self.arquivo  = arquivo

    def conectar( self ):

        p              = Pacote()
        p.construir_pacote(12345,0,0,2,"testando 123 testando,")
        self.sock.sendto(p.para_rede(), ("",self.port))
        msg_recebida,_ = self.sock.recvfrom(524)           
        p.desfazer_pacote( msg_recebida )
        self.port = int(p.dados)
        print(self.port)
        print("recebi conexao, pacote = ", p.mostra_dados())

    def mandar_arquivo( self ):
        
        with open( self.arquivo ) as arq:
            while(True):
                texto = arq.read(512)
                if(not texto):
                    break
                p              = Pacote()
                p.construir_pacote(12345,0,0,0,texto)
                self.sock.sendto(p.para_rede(), ("",self.port))
                msg_recebida,_ = self.sock.recvfrom(524)           
                p.desfazer_pacote( msg_recebida )
                print("recebi conexao, pacote = ", p.mostra_dados())
                
        
    def fechar_conexao(self, parameter_list):
        pass

c = Cliente(port,arquivo)
c.conectar()
c.mandar_arquivo()
