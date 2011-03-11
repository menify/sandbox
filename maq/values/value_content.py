
import array

class   _Checksum (object):
    __slots__ = ('offset', 'size', 'raw_data', 'checksum')
    
    def   __init__( self, offset, size ):
        self.offset = offset
        self.size = size

class   ValueContent (object):
    
    __slots__ = ( 'checksums' )
    
    def   __init__( self ):
        self.checksums = []
    
    #//-------------------------------------------------------//
    
    def   modified( self, other ):
        return False
    
    #//-------------------------------------------------------//
    
    def   serialize( self ):
        return str()
    
    #//-------------------------------------------------------//
    
    @classmethod
    def   restore( cls, state ):
        return cls();
   
    
    #//-------------------------------------------------------//
    
    def   __lt__( self, other):       return False
    def   __le__( self, other):       return False
    def   __eq__( self, other):       return False
    def   __ne__( self, other):       return False
    def   __gt__( self, other):       return False
    def   __ge__( self, other):       return False
