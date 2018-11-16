from socket    import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
from tools     import make_pkt, unpack, is_ack_of
from threading import Thread, Event


class HandleClient( Thread ):
    '''
    Handle client connection
    '''
    def __init__( self, client_id, address, udp_port , file_dir ):
        self.client_id       = client_id
        self.address         = address    
        self.udp_port        = udp_port
        self.file_dir        = file_dir
        self.close_connection= Event()  
        self.window          = TransferWindow()  
        Thread.__init__( self )

    def run( self ):
        self.conn = socket( AF_INET, SOCK_DGRAM )
        self.conn.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
        self.conn.bind( ( "", self.udp_port ) )

        self.send_pkt_syn_ack()

        file = open( self.file_dir + str( self.client_id ) + ".file" ,"w" )
        previous_pkt =  pkt_FIN = {}
        isFIN = False

        while( not self.close_connection.is_set() ):
            data, _          = self.conn.recvfrom( 524 )
            pkt = unpack( data )          
            
            if( isFIN and is_ack_of( pkt['ack_number'] , pkt_FIN['seq_number'] ) ):
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
    '''
    Handle all client connections
    '''    
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
        self.sock.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind( ( "", self.udp_port ) )
        
        while( not self.close_connection.is_set() ):
            data, addr = self.sock.recvfrom( 524 )
            pkt = unpack( data )
            print( "Received : ", pkt )
            
            if( not pkt['SYN'] ):
                continue

            hc = HandleClient( client_id, addr, udp_port_client, self.file_dir )
            hc.start()

            self.clients.append( hc )
            client_id       += 1
            udp_port_client += 1

    
    def close_all_connections( self ):
        pass


class ConnectionToServer():
    '''
    pass
    '''
    def __init__( self, server_address, filename):
        self.server_address= server_address
        self.filename      = filename
        self.seq_num       = 12345
        self.id            = 0
        self.conn          = socket( AF_INET, SOCK_DGRAM )
        self.window        = TransferWindow()
        self.conn.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)              

    def connect_to_server( self ):
        self.send_pkt_syn()
        self.wait_for_syn_ack()

    def send_pkt_syn( self ):
        pkt = make_pkt( seq_number=self.seq_num, connection_id=self.id, SYN=1 )
        self.send_pkt( pkt )
    
    def wait_for_syn_ack( self ):
        while( True ):
            data, addr = self.conn.recvfrom( 524 )
            pkt = unpack( data )

            if( pkt['ACK'] and pkt['SYN'] and is_ack_of( pkt['ACK'], self.seq_num) ):
                self.set_connection_options( pkt, addr )
                print('Received ack and syn.')
                break
            else:
                print('Not received ack and syn.')
    
    def set_connection_options( self, pkt_syn_ack, server_addr):
        self.server_address = server_addr
        self.id             = pkt_syn_ack['connection_id']
        self.seq_num        = pkt_syn_ack['ACK']
        self.ack_num        = pkt_syn_ack['seq_number'] + 1
    
    def send_pkt(self, pkt):
        self.conn.sendto( pkt, self.server_address)
    
    def send_initial_pkt( self ):
        text = self.file.read( 512 )
        pkt  = make_pkt( self.seq_num, self.ack_num, self.id, ACK=1 , data=text)
        self.send_pkt( pkt )
        self.window.buffer.append( pkt )
        # start_time()
        self.window.next_seq_num += 1
        self.seq_num += 12 + len( text )
    
    def send_file( self ):
        self.file = open( self.filename )
        self.send_initial_pkt()

        while( True ):
            if( self.window.can_send_pkt() ):
                text = self.file.read( 512 )

                if( not text ):
                    break

                pkt = make_pkt( self.seq_num, self.ack_num, self.id, data=text )
                self.send_pkt( pkt )
                self.window.buffer.append( pkt )
                
                if( self.window.base_equal_next_seq_num() ):
                    # start_time()
                    pass

                self.window.next_seq_num += 1
                # self.wait_for_ack_to( pkt )
        self.file.close()

    def wait_for_ack_to( self, package ):
        data, _ = self.conn.recvfrom( 524 )           
        pkt = unpack( data )

        if( pkt['ACK'] and is_ack_of( pkt['ack_number'], package['seq_number'] ) ):
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


class TransferWindow:

    def __init__( self, next_seq_num=1, base=1, cwnd=512, buffer=[] ):
        self.next_seq_num = next_seq_num
        self.base         = base
        self.cwnd         = cwnd
        self.buffer       = buffer
    
    def base_equal_next_seq_num( self ):
        return self.base == self.next_seq_num

    def can_send_pkt( self ):
        return self.next_seq_num < self.base + self.cwnd