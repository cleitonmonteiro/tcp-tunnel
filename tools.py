from ctypes import c_int, c_short
from sys import byteorder


def make_pkt( seq_number=0, ack_number=0, connection_id=0, ACK=0, SYN=0, FIN=0, data='' ):
    '''
    make
    '''
    return \
        bytes( c_int( seq_number ) ) + \
        bytes( c_int( ack_number ) ) + \
        bytes( c_short( connection_id ) ) + \
        bytes_options( ACK, SYN, FIN ) + \
        data.encode( 'utf-8' )

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
        'data'          : bytes_data.decode( 'utf-8' )
    }

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

def is_ack( bytes_data ):
    '''
    pass
    '''
    if( int.from_bytes( bytes_data[10:12], byteorder ) >= 4 ):
        return 1
    
    return 0

def is_syn( bytes_data ):
    '''
    pass
    '''
    if( int.from_bytes( bytes_data[10:12], byteorder ) >= 2 ):
        return 1
    
    return 0

def is_fin( bytes_data ):
    '''
    pass
    '''
    if( int.from_bytes( bytes_data[10:12], byteorder ) >= 1 ):
        return 1
    
    return 0

def is_ack_of( ack_number, seq_number ):
    '''
    ack of
    '''
    if( ack_number - 1 == seq_number ):
        return True
    return False