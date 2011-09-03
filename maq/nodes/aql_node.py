
from aql_utils import toSequence

class Node (object):
  
  __slots__ = \
  (
    'builder',
    'source_values',
    'source_nodes',
    'depend_values',
    'depend_nodes',
    'target_values',
    'side_effect_values',
    'implicit_depend_values',
    'implicit_depend_nodes',
  )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, builder, sources ):
    self.builder = builder
    
    for source in toSequence( sources ):
      if isintance()
    
    self.builder = builder
    
  
  #//-------------------------------------------------------//
  
  def   __getstate__( self ):
    state = {}
    for attr in self.__slots__:
      try:
        state[ attr ] = getattr( self, attr )
      except AttributeError:
        pass
    
    return state
  
  #//-------------------------------------------------------//
  
  def   __setstate__( self, state ):
    for attr,value in state.items():
      setattr( self, attr, value )
  
  #//-------------------------------------------------------//
  
