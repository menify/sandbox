
from aql_value import Value

#//===========================================================================//

StringContent = str

class   StringContentIgnoreCase (str):
    
  def   __eq__( self, other ):
    return type(self) == type(other) and \
      (self.lower() == other.lower())
  
  def   __ne__( self, other ):        return not self.__eq__( other )

#//===========================================================================//

class StringValue (Value):
  def   __init__(self, name, content = None ):
    if isinstance( name, Value ):
      other = name
      name = other.name
      
      if content is None:
        content = other.content
    
    super().__init__( name, content )


#//===========================================================================//
