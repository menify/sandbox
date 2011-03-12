
import hashlib

class   ValueContent (object):
    
    __slots__ = ( 'checksums' )
    
    def   __init__( self, data ):
        checksum = hashlib.md5()
        
        for chunk in data:
            checksum.update( chunk )
        
        self.checksum = checksum
    
    #//-------------------------------------------------------//
    
    def   __eq__( self, other ):          return self.checksum == other.checksum
    def   __ne__( self, other ):          return self.checksum != other.checksum
    def   __getstate__( self ):           return { 'checksum': self.checksum }
    def   __setstate__( self, state ):    self.checksum = state['checksum']
