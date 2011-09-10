
from aql_hash import Hash

class ItemManager (object):
  
  __slots__ = ('item_type', 'hash')
  
  #//-------------------------------------------------------//
  
  def   __init__(self, item_type):
    self.hash = Hash()
  
  #//-------------------------------------------------------//
  
  def   addItem( self, item ):
    
    item = self.hash( *args, **kw )
    
    return self.hash.add( item )
  
  def   save
