
class   Value (object):
    
    def   __init__( self ):
        pass
    
    #//-------------------------------------------------------//
    
    def   modified( self, other ):
        return False
    
    #//-------------------------------------------------------//
    
    def   to_bytes( self ):
        return str()
    
    #//-------------------------------------------------------//
    
    @classmethod
    def   from_bytes( cls, bytes ):
        return cls();
   
    
    #//-------------------------------------------------------//
    
    def   __lt__( self, other):       return False
    def   __le__( self, other):       return False
    def   __eq__( self, other):       return False
    def   __ne__( self, other):       return False
    def   __gt__( self, other):       return False
    def   __ge__( self, other):       return False
