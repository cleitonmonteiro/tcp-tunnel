from socket    import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
from tools     import make_pkt, unpack, is_ack_of, show_pkt, len_pkt,TransferWindow
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
        self.seq_num         = 4321
        self.ack_num         = 12346
        self.close_connection= Event()  
        self.window          = TransferWindow()
        self.data_to_send_acks    = []  
        Thread.__init__( self )

    def run( self ):
        self.conn = socket( AF_INET, SOCK_DGRAM )
        self.conn.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)
        self.conn.bind( ( "", self.udp_port ) )

        self.send_pkt_syn_ack()

        file = open( self.file_dir + str( self.client_id ) + ".file" ,"wb" )
        pkt_FIN = {}
        isFIN = False

        while( not self.close_connection.is_set() ):
            
            data, _ = self.conn.recvfrom( 524 )
            print("[<==] ",end=" ")
            show_pkt(data)
            pkt     = unpack( data )        
              
            
            if( isFIN and is_ack_of( pkt, pkt_FIN ) ):
                file.close()
                break

            if( pkt['FIN'] ):
                isFIN = True
                pkt_FIN = self.close_tcp_connection( pkt )
            else:
                self.clear_buff( pkt )
                if( self.duplicate_ack( pkt ) ):
                    make_pkt(self.data_to_send_acks[-1])
                    self.send_pkt( self.data_to_send_acks[-1] )
                else:
                    # self.window.buff.append( pkt )
                    file.write( pkt['data'] )
                    self.seq_num = pkt['ack_number']
                    self.ack_num = pkt['seq_number'] + len_pkt( pkt )
                    pkt = make_pkt(seq_number=self.seq_num, ack_number=self.ack_num, connection_id=self.client_id, ACK=1)
                    self.send_pkt( pkt )
                    pkt = unpack( pkt )
                    self.data_to_send_acks.append( pkt )

    def clear_buff( self , pkt ):
        if ( self.data_to_send_acks and pkt['seq_number'] == 0 ):
            print('clear')
            self.data_to_send_acks = self.data_to_send_acks[-1:]

    def duplicate_ack( self, pkt ):
        if(not self.data_to_send_acks):
            return False
        if( self.data_to_send_acks[-1]['ack_number'] + 512 > 102400):
            return False

        if( pkt['seq_number'] == self.data_to_send_acks[-1]['ack_number']):
            return False
        return True
        
    def send_pkt_syn_ack( self ):    
        pkt = make_pkt( seq_number=self.seq_num, ack_number=self.ack_num, connection_id=self.client_id, SYN=1, ACK=1 )
        self.send_pkt( pkt )
        #self.window.buff.append(pkt)

    def close_tcp_connection( self , pkt_fin ):    
        pkt = make_pkt( 4322, pkt_fin['seq_number'] + len_pkt( pkt_fin ), self.client_id, ACK=1)
        self.send_pkt( pkt )

        pkt = make_pkt( connection_id=self.client_id, FIN=1)
        self.send_pkt( pkt )
    
        return unpack( pkt )

    def send_pkt(self, pkt):
        print("[==>] ",end=" ")
        show_pkt(pkt)
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
        try:
            while( True ):
                data, addr = self.sock.recvfrom( 524 )
                print("[<==] ",end=" ")
                show_pkt(data)
                pkt = unpack( data )
                
                if( self.close_connection.is_set() ):
                    break
                
                if( not pkt['SYN'] ):
                    continue

                hc = HandleClient( client_id, addr, udp_port_client, self.file_dir )
                hc.start()

                self.clients.append( hc )
                client_id       += 1
                udp_port_client += 1
        except KeyboardInterrupt:
            pass

    def close_all_connections( self ):
        pass
        # self.close_connection.set()
        # self.sock.close()
        # self.sock.shutdown(0)
