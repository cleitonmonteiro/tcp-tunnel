import                socket
import                sys
import                threading 
from cabecalho import Pacote


port = int(sys.argv[1])
armazenar = ""
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(("", port))

conexoes = []

class Manter_cliente(threading.Thread):
    def __init__(self,conexao,numero_conexao,endereco):
        threading.Thread.__init__(self)
        self.conexao = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.numero_conexao = numero_conexao
        self.endereco = endereco
    def enviar_pacote_inicio(self):
        p = Pacote()
        p.construi_pacote(4321,123456,self.numero_conexao,6)
        self.conexao.sendto(p.para_rede(),self.endereco)
    def enviar_pacote_geral(self, seq, ack):
        p = Pacote()
        p.construi_pacote(seq,ack,self.numero_conexao,2)
        self.conexao.sendto(p.para_rede(),self.endereco)
    def run(self):
        self.enviar_pacote_inicio()
        while(True):
            dados,_ = self.conexao.recvfrom(524)
            p = Pacote()
            p.desfazer_pacote()


        


class EsperarCliente(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run():
        data, addr = sock.recvfrom(524)
        p = Pacote()
        p.desfazer_pacote(data)
        print("Received message: ",p.mostradados())

    
