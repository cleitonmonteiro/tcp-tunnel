from socket     import socket, AF_INET, SOCK_DGRAM
from tools      import make_pkt, unpack, isACK_of
from threading  import Thread, Event


class HandleClient( Thread ):
    
    def __init__( self, client_id, address, udp_port , file_dir ):
        self.client_id       = client_id
        self.address         = address    
        self.udp_port        = udp_port
        self.file_dir        = file_dir
        self.close_connection= Event()    
        Thread.__init__( self )

    def run( self ):
        self.conn = socket( AF_INET, SOCK_DGRAM )
        self.conn.bind( ( "", self.udp_port ) )

        self.send_pkt_syn_ack()

        file = open( self.file_dir + str( self.client_id ) + ".file" ,"w" )
        previous_pkt =  pkt_FIN = {}
        isFIN = False

        while( not self.close_connection.is_set() ):
            data, _          = self.conn.recvfrom( 524 )
            pkt = unpack( data )          
            
            if( isFIN and isACK_of( pkt , pkt_FIN ) ):
                file.close()
                break
    
            if( pkt['FIN'] ):
                isFIN = True
                pkt_FIN = self.close_tcp_connection()
            else:
                file.write( pkt['data'] )
                pkt = make_pkt(seq_number=666, ACK=1, data="RECEIVED")
                self.send_pkt( pkt )
            
            previous_pkt = pkt
        
        self.close()
    
    def send_pkt_syn_ack( self ):    
        pkt = make_pkt( seq_number=4321, ack_number=12346, connection_id=self.client_id, SYN=1, ACK=1 )
        self.send_pkt( pkt )
    
    def close_tcp_connection( self ):
        pkt = make_pkt( connection_id=self.client_id, ACK=1)
        self.send_pkt( pkt )

        pkt = make_pkt( connection_id=self.client_id, FIN=1)
        self.send_pkt( pkt )
    
        return pkt

    def send_pkt(self, pkt):
        self.conn.sendto( pkt, self.address)

    def close( self ):
        pass


class HandleConnection( Thread ):
    
    def __init__( self, udp_port, filer_dir, clients):
        self.udp_port        = udp_port
        self.file_dir        = filer_dir
        self.clients         = clients
        self.close_connection= Event()
        Thread.__init__( self )

    def run( self ):
        client_id           = 1
        udp_port_client     = 5000
        self.sock           = socket( AF_INET, SOCK_DGRAM )
        self.sock.bind( ( "", self.udp_port ) )
        
        while( not self.close_connection.is_set() ):
            data, addr = self.sock.recvfrom( 524 )
            pkt = unpack( data )
            print( "Received : ", pkt )

            hc = HandleClient( client_id, addr, udp_port_client, self.file_dir )
            hc.start()

            self.clients.append(hc)
            client_id       += 1
            udp_port_client += 1

        self.close_all_connections()
    
    def close_all_connections( self ):
        pass


class ConnectionToServer():

    def __init__( self, server_address, filename):
        self.server_address= server_address
        self.filename      = filename
        self.id            = 0
        self.conn          = socket(AF_INET, SOCK_DGRAM)

    def connect_to_server( self ):
        self.send_pkt_syn()
        self.wait_for_syn_ack()

    def send_pkt_syn( self ):    
        pkt = make_pkt( seq_number=12345, connection_id=self.id, SYN=1 )
        self.send_pkt( pkt )
    
    def wait_for_syn_ack( self ):
        data, addr = self.conn.recvfrom(524)           
        pkt = unpack( data )

        if( pkt['ACK'] and pkt['SYN'] ):
            self.server_address = addr
            self.id             = pkt['connection_id']
            print('Received ack and syn.')
        else:
            print('Not received ack and syn.')
            self.wait_for_syn_ack()

    def send_pkt(self, pkt):
        self.conn.sendto( pkt, self.server_address)
        
    def send_file( self ):        
        with open( self.filename ) as file:
            while( True ):
                text = file.read(512)
                if( not text ): break
                pkt = make_pkt( connection_id=self.id, data=text )
                self.send_pkt( pkt )
                self.wait_for_ack_to( pkt )

    def wait_for_ack_to( self, package ):
        data, _ = self.conn.recvfrom( 524 )           
        pkt = unpack( data )

        if( pkt['ACK'] and isACK_of( pkt, package ) ):
            print('Received ack to pkt: ', package )
        else:
            print('Not received ack to pkt: ', package )
            self.wait_for_ack_to( package )
        
    def close( self ):
        pkt = make_pkt( FIN=1 )
        self.send_pkt( pkt )
        self.wait_for_ack_to( pkt )
        self.wait_for_fin()
    
    def wait_for_fin( self ):
        data, _ = self.conn.recvfrom( 524 )           
        pkt = unpack( data )

        if( pkt['FIN'] ):
            print('Received pkt fin.')
        else:
            print('Not received pkt fin.')
            self.wait_for_fin()
