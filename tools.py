from ctypes import c_int, c_short
from sys import byteorder


def make_pkt( seq_number=0, ack_number=0, connection_id=0, ACK=0, SYN=0, FIN=0, data='' ):
    return \
        bytes( c_int( seq_number ) ) + \
        bytes( c_int( ack_number ) ) + \
        bytes( c_short( connection_id ) ) + \
        bytes_options( ACK, SYN, FIN ) + \
        data.encode( 'utf-8' )

def unpack( bytes_data ):
    return {
        'seq_number'    : int.from_bytes( bytes_data[:4], byteorder ),
        'ack_number'    : int.from_bytes( bytes_data[4:8], byteorder ),
        'connection_id' : int.from_bytes( bytes_data[8:10], byteorder ),
        'ACK'         :  isACK( bytes_data ),
        'SYN'         :  isSYN( bytes_data ),
        'FIN'         :  isFIN( bytes_data ),
        'data'          : bytes_data.decode( 'utf-8' )
    }

def bytes_options( ACK, SYN, FIN ):
    if( SYN and ACK):
        return bytes(c_short(6))
    
    if( SYN ):
        return bytes(c_short(2))
    
    if( FIN ):
        return bytes(c_short(1))
    
    if( ACK ):
        return bytes(c_short(4))

def isACK( bytes_data ):
    if( int.from_bytes( bytes_data[10:12], byteorder ) >= 4 ):
        return 1
    
    return 0

def isSYN( bytes_data ):
    if( int.from_bytes( bytes_data[10:12], byteorder ) >= 2 ):
        return 1
    
    return 0

def isFIN( bytes_data ):
    if( int.from_bytes( bytes_data[10:12], byteorder ) >= 1 ):
        return 1
    
    return 0

def isACK_of( pkt, previous_pkt ):
    if( pkt['ack_number']-1 == previous_pkt['seq_number'] ):
        return True
    return False