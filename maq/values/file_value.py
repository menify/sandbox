
import Value
import hashlib

#//===========================================================================//

class   FileContent (object):
    
    __slots__ = ( 'checksums' )
    
    def   __init__( self, path ):
        
        checksum = hashlib.md5()
        
        for chunk in open( path, mode = 'rb' ):
            checksum.update( chunk )
        
        self.checksum = checksum
    
    #//-------------------------------------------------------//
    
    def   __eq__( self, other ):          return self.checksum == other.checksum
    def   __ne__( self, other ):          return self.checksum != other.checksum
    def   __getstate__( self ):           return { 'checksum': self.checksum }
    def   __setstate__( self, state ):    self.checksum = state['checksum']

#//===========================================================================//

class   File (Value):
    
    __slots__ = ( 'path', 'size', 'content' )
    
    def   __init__( self, path, content = FileContent ) :
        self.path = os.path.abspath( path )
        self.content = content( path )
    
    #//-------------------------------------------------------//
    
    def   modified( self, other ):
        return False
    
    #//-------------------------------------------------------//
    
    def   __( self ):
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
