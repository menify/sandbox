
from aql_hash import Hash

class ItemManager (object):
  
  __slots__ = ('item_type', 'hash')
  
  #//-------------------------------------------------------//
  
  def   __init__(self, item_type):
    self.item_type = item_type
    self.hash = Hash()
  
  #//-------------------------------------------------------//
  
  def   createItem( self, *args, **kw ):
    
    item = self.item_type( *args, **kw )
    
    return self.hash.add( item )
  
  def   save
