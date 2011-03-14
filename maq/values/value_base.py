
class   ValueBase (object):
    
    def   __init__( self ):
        pass
    
    #//-------------------------------------------------------//
    
    def   __getstate__( self ):
        return {}
    
    #//-------------------------------------------------------//
    
    def   __setstate__( self, state ):
        pass
   
    
    #//-------------------------------------------------------//
    
    def   __lt__( self, other):       return False
    def   __le__( self, other):       return False
    def   __eq__( self, other):       return False
    def   __ne__( self, other):       return False
    def   __gt__( self, other):       return False
    def   __ge__( self, other):       return False
