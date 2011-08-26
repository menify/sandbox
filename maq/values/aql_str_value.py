
from aql_value import Value

#//===========================================================================//

StringContent = str
StringValue = Value

class   StringContentIgnoreCase (str):
    
  def   __eq__( self, other ):
    return type(self) == type(other) and \
      (self.lower() == other.lower())
  
  def   __ne__( self, other ):        return not self.__eq__( other )

#//===========================================================================//
