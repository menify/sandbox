
class   Value (object):
    
    __slots__ = ( 'name', 'content' )
    
    def   __init__( self, name, content ) :
        self.name = name
        self.content = content
    
    #//-------------------------------------------------------//
    
    def   __getstate__( self ):
        return { 'name': self.name, 'content' : self.content }
    
    #//-------------------------------------------------------//
    
    def   __setstate__( self, state ):
        self.name = state['name']
        self.content = state['content']
    
    #//-------------------------------------------------------//
    
    def   __lt__( self, other):       return self.name < other.name
    def   __le__( self, other):       return self.name <= other.name
    def   __eq__( self, other):       return self.name == other.name
    def   __ne__( self, other):       return self.name != other.name
    def   __gt__( self, other):       return self.name > other.name
    def   __ge__( self, other):       return self.name >= other.name
    
    #//-------------------------------------------------------//
    
    def   __str__(self):    return str(self.name) + ", " + str(self.content)
