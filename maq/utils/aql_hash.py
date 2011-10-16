import uuid

class Hash (object):
  
  __slots__ = ('pairs', 'seq_num', 'keys')
  
  def   __init__(self):
    
    self.pairs = {}
    self.seq_num = 0
    self.keys = {}
  
  #//-------------------------------------------------------//
  
  def   findRef( self, item ):
    pairs = self.pairs.setdefault( hash(item), [] )
    
    index = 0
    for value_key, value_item in pairs:
      if value_item == item:
        return pairs, index
      
      index += 1
    
    return pairs, -1
    
  #//-------------------------------------------------------//
  
  def   addToRef( self, ref, key, item ):
    
    pairs, index = ref
    pair = (key, item )
    
    keys = self.keys
    
    if index != -1:
      old_key = pairs[index][0]
      del keys[ old_key ]
      pairs[ index ] = pair
    
    else:
      pairs.append( pair )
    
    keys[ key ] = item
    
  #//-------------------------------------------------------//
  
  def   removeByRef( self, ref ):
    pairs, index = ref
    if index != -1:
      key = pairs[index][0]
      del self.keys[ key ]
      del pairs[ index ]
  
  #//-------------------------------------------------------//
  
  def   __delitem__( self, key ):
    item = self.keys[ key ]
    self.remove( item )
  
  #//-------------------------------------------------------//
  
  def   __getitem__(self, key):
    return self.keys[ key ]
  
  #//-------------------------------------------------------//
  
  def   __setitem__(self, key, item ):
    
    try:
      old_item = self.keys[ key ]
      self.remove( old_item )
    except KeyError:
      pass
    
    ref = self.findRef( item )
    self.addToRef( ref, key, item )
  
  #//-------------------------------------------------------//
  
  def   getKey( self, ref ):
    pairs, index = ref
    if index != -1:
      return pairs[index][0]
    
    return None
  
  #//-------------------------------------------------------//
  
  def   getKeyItem( self, ref ):
    pairs, index = ref
    if index != -1:
      pair = pairs[index]
      return pair
    
    return None
  
  #//-------------------------------------------------------//
  
  def   getItem( self, ref ):
    pairs, index = ref
    if index != -1:
      return pairs[index][1]
    
    return None
  
  #//-------------------------------------------------------//
  
  def   find(self, item):
    pairs, index = self.findRef( item )
    if index != -1:
      return pairs[index]
    
    return None, None
  
  #//-------------------------------------------------------//
  
  def   remove(self, item):
    ref = self.findRef( item )
    key = self.getKey( ref )
    
    self.removeByRef( ref )
    
    return key
  
  #//-------------------------------------------------------//
  
  def   __contains__(self, item):
    return self.find( item )[1] is not None
  
  #//-------------------------------------------------------//
  
  def   __iter__(self):
    for key, item in self.keys.items():
      yield item
  
  #//-------------------------------------------------------//
  
  def   clear(self):
    self.pairs.clear()
    self.keys.clear()
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return len(self.keys)
  
  #//-------------------------------------------------------//
  
  def   __bool__(self):
    return bool(self.keys)
  
  #//-------------------------------------------------------//
  
  def   selfTest( self ):
    size = 0
    for item_id, pairs in self.pairs.items():
      for key, item in pairs:
        size += 1
        
        if hash(item) != item_id:
          raise AssertionError("hash(item) != item_id")
        
        if key not in self.keys:
          raise AssertionError("key not in self.keys")
        
        if item is not self.keys[ key ]:
          raise AssertionError("item is not self.keys[ key ]")
    
    if size != len(self.keys):
      raise AssertionError("size != len(self.keys)")
