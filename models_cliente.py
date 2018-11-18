from socket    import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR
from tools     import make_pkt, unpack, is_ack_of, show_pkt, len_pkt,TransferWindow
from threading import Thread, Event

class ConnectionToServer():
    '''
    pass
    '''
    def __init__( self, server_address, filename):
        self.server_address= server_address
        self.filename      = filename
        self.seq_num       = 12345
        self.ack_num       = 0
        self.id            = 0
        self.conn          = socket( AF_INET, SOCK_DGRAM )
        self.window        = TransferWindow()
        self.recved_acks   = []
        self.c_rtrss_pkt   = 0
        self.c_duplicate_pkt= 0
        self.conn.setsockopt( SOL_SOCKET, SO_REUSEADDR, 1)              

    def connect_to_server( self ):
        self.send_pkt_syn()
        self.wait_for_syn_ack()

    def send_file( self ):
        self.file = open( self.filename, "rb")
        self.send_initial_pkt()

        while( True ):

            self.recv_ack_pkt()
            
            if( self.window.can_send_pkt() ):
                text = self.file.read( 512 )
                if( not text ):
                    break

                pkt = make_pkt( self.seq_num, connection_id=self.id, data=text )
                self.send_pkt( pkt )
                pkt = unpack( pkt )
                self.window.buff.append( pkt )
                
                if( self.window.base_equal_next_seq_num() ):
                    # start_time()
                    pass

                self.update_window( )


        self.file.close()

    def close( self ):
        pkt = make_pkt( self.seq_num, self.ack_num, connection_id=self.id, FIN=1 )
        self.send_pkt( pkt )
        pkt = unpack( pkt )
        self.window.buff.append( pkt )
        self.wait_ack_of_fin()
        self.wait_for_fin()
        print("d Number of duplicate packages :", self.c_duplicate_pkt)

    def send_pkt_syn( self ):
        pkt = make_pkt( seq_number=self.seq_num, connection_id=self.id, SYN=1 )
        self.send_pkt( pkt )
    
    def wait_for_syn_ack( self ):
        while( True ):
            data, addr = self.conn.recvfrom( 524 )
            print("[<==] ",end=" ")
            show_pkt(data)
            pkt = unpack( data )
            
            if( pkt['ACK'] and pkt['SYN'] ):
                self.set_connection_options( pkt, addr )
                print('Received ack and syn.')
                self.ack_num = pkt['seq_number'] + 1
                self.seq_num = pkt['ack_number']
                break
            else:
                print('Not received ack and syn.')
    
    def set_connection_options( self, pkt_syn_ack, server_addr):
        self.server_address = server_addr
        self.id             = pkt_syn_ack['connection_id']
        self.seq_num        = pkt_syn_ack['ACK']
        self.ack_num        = pkt_syn_ack['seq_number'] + 1
    
    def send_pkt( self, pkt ):
        self.conn.sendto( pkt, self.server_address )
        print("[==>] ",end=" ")
        show_pkt( pkt )
    
    def update_window( self):
        self.window.next_seq_num += 1
        # self.ack_num = self.window.buff[-1]['seq_number'] + 1
        self.seq_num += len_pkt( self.window.buff[-1] )
        if( self.seq_num > 102400):
            self.seq_num = 0
            # self.ack_num = 0

    def send_initial_pkt( self ):
        text = self.file.read( 512 )
        pkt  = make_pkt( self.seq_num, self.ack_num, self.id, ACK=1 , data=text )
        self.send_pkt( pkt )
        pkt = unpack( pkt )
        self.window.buff.append( pkt )
        # start_time()
        self.update_window( )

    def recv_ack_pkt( self ):
        # print( self.window )
        
        def duplicate_ack( pkt ):
            if( self.recved_acks.count( pkt['ack_number'] ) == 4):
                return True
            return False

        def index_pkt_ack( pkt ):
            for i, p in enumerate( self.window.buff ):
                if( pkt['ACK'] and is_ack_of( pkt, p )):
                    self.recved_acks.append(p['ack_number'])
                    return i + 1
        # self.conn.settimeout( 0.1 )
        # try:
        data, _ = self.conn.recvfrom( 524 )
        # except:
        #     self.c_rtrss_pkt += 1
        # self.conn.settimeout(None)
        
        if ( self.c_rtrss_pkt == 5):
            print('===== Start retranmission')
            for p in self.window.buff[self.window.base:self.window.next_seq_num]:
                pkt = make_pkt( p['seq_number'], p['ack_number'], p['connection_id'], data=p['data'])
                self.send_pkt( pkt )

        print( "[<==] ",end=" ")
        show_pkt(data)
        pkt     = unpack( data )
        index   = index_pkt_ack( pkt )        

        if( index ):
            if( duplicate_ack( pkt ) ):
                self.resend_pkt( index + 1 )
                self.window.ssthresh = self.window.size*512 // 2
                self.window.set_default()
                self.c_duplicate_pkt += 1
            else:
                self.window.base = index
                if( self.window.size*512 < self.window.ssthresh ):
                    self.window.size *= 2
                else:
                    self.window.size += 1

    def resend_pkt( self, index ):
        pkt = self.window.buff[index]
        self.send_pkt( pkt )
    
    def wait_ack_of_fin( self ):
        while(True):
            data, _ = self.conn.recvfrom( 524 )           
            print("[<==] ",end=" ")
            show_pkt( data )
            pkt = unpack( data )


            if( pkt['ACK'] and is_ack_of(pkt, self.window.buff[-1])):
                print('Received ACK of FIN.')
                break
            else:
                print('Not received ACK pkt of FIN.')
        
    def send_pkt_ack_for_fin( self, pkt ):
        self.window.buff.append( pkt )
        self.update_window()
        n_pkt = make_pkt( self.seq_num, self.ack_num, self.id,ACK=1 )
        self.send_pkt( n_pkt )

    def wait_for_fin( self ):
        while(True):
            data, _ = self.conn.recvfrom( 524 )           
            print("[<==] ",end=" ")
            show_pkt( data )
            pkt = unpack( data )

            if( pkt['FIN'] ):
                self.send_pkt_ack_for_fin(pkt)
                print('Received pkt fin.')
                break
            else:
                print('Not received pkt fin.')
                



