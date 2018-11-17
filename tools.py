from ctypes import c_int, c_short
from sys import byteorder


def make_pkt( seq_number=0, ack_number=0, connection_id=0, ACK=0, SYN=0, FIN=0, data=b'' ):
    '''
    make
    '''
    return \
        bytes( c_int( seq_number ) ) + \
        bytes( c_int( ack_number ) ) + \
        bytes( c_short( connection_id ) ) + \
        bytes_options( ACK, SYN, FIN ) + \
        data

def unpack( bytes_data ):
    '''
    unpack
    '''
    return {
        'seq_number'    : int.from_bytes( bytes_data[:4], byteorder ),
        'ack_number'    : int.from_bytes( bytes_data[4:8], byteorder ),
        'connection_id' : int.from_bytes( bytes_data[8:10], byteorder ),
        'ACK'           :  is_ack( bytes_data ),
        'SYN'           :  is_syn( bytes_data ),
        'FIN'           :  is_fin( bytes_data ),
        'data'          : bytes_data[12:]
    }

def show_pkt( pkt ):
    pkt = unpack(pkt)
    print( list(pkt.values())[:-1], end=" - " )
    if( pkt['data'] ):
        print( "data" )
    else:
        print( "empty" )

def corrupt_pkt( pkt ):
    '''
    pass
    '''
    pass

def bytes_options( ACK, SYN, FIN ):
    '''
    '''
    if( SYN and ACK):
        return bytes(c_short(6))
    
    if( SYN ):
        return bytes(c_short(2))
    
    if( FIN ):
        return bytes(c_short(1))
    
    if( ACK ):
        return bytes(c_short(4))
    
    return bytes(c_short(0))

def is_ack( bytes_data ):
    '''
    pass
    '''
    if( bin(int.from_bytes( bytes_data[10:12], byteorder ))[-3] == "1" ):
        return 1
    
    return 0

def is_syn( bytes_data ):
    '''
    pass
    '''
    if( bin(int.from_bytes( bytes_data[10:12], byteorder ))[-2] == "1" ):
        return 1
    
    return 0

def is_fin( bytes_data ):
    '''
    pass
    '''
    if( bin(int.from_bytes( bytes_data[10:12], byteorder ))[-1] == "1" ):
        return 1
    
    return 0

def is_ack_of( ack_number, seq_number ):
    '''
    ack of
    '''
    if( ack_number - 1 == seq_number ):
        return True
    return False

def len_pkt( pkt ):
    '''
    '''
    if(type(pkt) is bytes):
        return len(pkt)
    return 12 + len(pkt['data'])

class TransferWindow:
    
    def __init__( self, next_seq_num=1, base=1, cwnd=512, buff=[] ):
        self.next_seq_num = next_seq_num
        self.base         = base
        self.cwnd         = cwnd
        self.buff         = buff
    
    def base_equal_next_seq_num( self ):
        return self.base == self.next_seq_num

    def can_send_pkt( self ):
        return self.next_seq_num < self.base + self.cwnd