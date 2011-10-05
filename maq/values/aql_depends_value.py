
from aql_value import Value

#//===========================================================================//

class   DependsValueContent (object):
  
  __slots__ = ( 'values', )
  
  def   __init__( cls, values = None ):
    
    if values is None:
      values = tuple()
    
    try:
      values = list(values)
    except TypeError:
      values = [values]
    
    values.sort()
    
  #//-------------------------------------------------------//
  
  def   __eq__( self, other ):
    if (type(self) != type(other)) or (self.values != other.values):
      return False
    
    for value1, value2 in zip( self.values, other.values ):
      if value1.content != value2.content:
        return False
    
    return True
  
  #//-------------------------------------------------------//
  
  def   __ne__( self, other ):
    return not self.__eq__( other )
  
  #//-------------------------------------------------------//
  
  def   __str__( self ):
    return str(self.values)
  
  #//-------------------------------------------------------//
  
  def   __getstate__( self ):
    raise Exception( "Object '%s' can't be serialized." % type(self).__name__ )
  
  #//-------------------------------------------------------//
  
  def   __setstate__( self, state ):
    raise Exception( "Object '%s' can't be de-serialized." % type(self).__name__ )


#//===========================================================================//

class   DependsValue (Value):
  
  def   __init__( self, name, content = None ):
    
    if isinstance( name, DependsValue ):
      other = name
      name = other.name
    
      if content is None:
        content = other.content
    
    super(FileValue, self).__init__( name, content )

#//===========================================================================//
