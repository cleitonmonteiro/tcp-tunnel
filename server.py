import                socket
import                sys
import                threading 
from cabecalho import Pacote


port      = int( sys.argv [1] )
armazenar = sys.argv[2]


class ManterCliente( threading.Thread ):
    
    def __init__( self, numero_conexao, endereco, port_cliente ):
        
        threading.Thread.__init__( self )
        self.conexao        = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.numero_conexao = numero_conexao
        self.endereco       = endereco    
        self.port_cliente   = port_cliente
    
    def enviar_pacote_inicio( self ):
    
        p = Pacote()
        p.construir_pacote( 4321, 123456, self.numero_conexao, 6,str(self.port_cliente))
        self.conexao.sendto( p.para_rede( ), self.endereco )
    
    def enviar_pacote_geral(self, seq, ack):
    
        p = Pacote()
        p.construi_pacote( seq ,ack ,self.numero_conexao, 2 )
        self.conexao.sendto( p.para_rede(), self.endereco )
    
    def finaliza_conexao( self ):
    
        p = Pacote()
    
        p.contruir_pacote( 0, 0, self.numero_conexao, 2 )
        self.conexao.sendto( p.para_rede(), self.endereco )
    
        p.contruir_pacote(0 ,0 ,self.numero_conexao, 1 )
        self.conexao.sendto( p.para_rede() , self.endereco )
    
        return p.mostra_dados()
    
    def run( self ):
        
        self.conexao.bind(("",self.port_cliente))
        self.enviar_pacote_inicio()
        arq = open( armazenar + str( self.numero_conexao ) + ".file" ,"w" )
        aux = None


        while( True ):
    
            dados,_          = self.conexao.recvfrom( 524 )
            p                = Pacote()
            p.desfazer_pacote(dados)
            aux_pacote_lista = p.mostra_dados()
            
            
            if( aux and aux_pacote_lista[1] - 1 == aux[0] ):
                break
    
            if( p.opcoes == 1 ):
                aux = self.finiza_conexao()
    
            else:
                arq.write( p.dados )
                p.construir_pacote(666,0,0,2,"recebi")
                self.conexao.sendto(p.para_rede(),self.endereco)
                


        


class EsperarCliente( threading.Thread ):
    def __init__( self ):
        threading.Thread.__init__( self )

    def run( self ):
        
        id_conexao   = 0
        port_cliente = 5000

        sock         = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        sock.bind( ( "", port ) )
        
        while( True ):
        
            data, addr = sock.recvfrom( 524 )
            p          = Pacote()
            p.desfazer_pacote( data )
            print("Received message: ",p.mostra_dados() )

            thread_do_cliente = ManterCliente( id_conexao, addr, port_cliente)
            thread_do_cliente.start()
            port_cliente     += 1
            id_conexao       += 1




thread_espera = EsperarCliente()
thread_espera.start()

