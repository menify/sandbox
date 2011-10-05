import uuid

class Hash (object):
  
  __slots__ = ('pairs', 'size', 'seq_num', 'keys')
  
  def   __init__(self):
    
    self.pairs = {}
    self.size = 0
    self.seq_num = 0
    self.keys = {}
  
  #//-------------------------------------------------------//
  
  def   __genKey(self):
    key = (self.seq_num, uuid.uuid4())
    self.seq_num += 1
    return key
  
  #//-------------------------------------------------------//
  
  def   __findItem( self, item ):
    pairs = self.pairs.setdefault( hash(item), [] )
    
    index = 0
    for value_key, value_item in pairs:
      if value_item == item:
        return pairs, index
      
      index += 1
    
    return pairs, -1
    
  #//-------------------------------------------------------//
  
  def   __addItem( self, pairs, key, item ):
    pair = (key, item)
    
    pairs.append( pair )
    self.keys[ key ] = item
    
    self.size += 1
    
    return pair
    
  #//-------------------------------------------------------//
  
  def   __removeItem( self, pairs, index, key ):
    del self.keys[ key ]
    del pairs[ index ]
    
    self.size -= 1
  
  #//-------------------------------------------------------//
  
  def   __updateItem( self, pairs, index, key, item ):
    
    pair = (key, item )
    old_key = pairs[index][0]
    del self.keys[ old_key ]
    pairs[ index ] = pair
    self.keys[ key ] = item
    
    return old_key
  
  #//-------------------------------------------------------//
  
  def   __delitem__( self, key ):
    item = self.keys[ key ]
    self.remove( item )
  
  #//-------------------------------------------------------//
  
  def   __getitem__(self, key):
    return self.keys[ key ]
  
  #//-------------------------------------------------------//
  
  def   __setitem__(self, key, item ):
    
    if key in self.keys:
      del self[ key ]
    
    pairs, index = self.__findItem( item )
    if index == -1:
      self.__addItem( pairs, key, item )
    else:
      self.__updateItem( pairs, index, key, item )
  
  #//-------------------------------------------------------//
  
  def   find(self, item):
    pairs, index = self.__findItem( item )
    if index != -1:
      return pairs[index]
    
    return None, None
  
  #//-------------------------------------------------------//
  
  def   add( self, item ):
    
    pairs, index = self.__findItem( item )
    if index != -1:
      return pairs[index]
    
    return self.__addItem( pairs, self.__genKey(), item )
  
  #//-------------------------------------------------------//
  
  def   update( self, item ):
    key = self.__genKey()
    old_key = None
    
    pairs, index = self.__findItem( item )
    if index == -1:
      self.__addItem( pairs, key, item )
    else:
      old_key = self.__updateItem( pairs, index, key, item )
    
    return key, old_key
  
  #//-------------------------------------------------------//
  
  def   remove(self, item):
    
    pairs, index = self.__findItem( item )
    if index != -1:
      key = pairs[index][0]
      self.__removeItem( pairs, index, key )
      return key
    
    return None
  
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
    self.size = 0
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return self.size
  
  #//-------------------------------------------------------//
  
  def   __bool__(self):
    return self.size > 0
  
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
    
    if size != self.size:
      raise AssertionError("size != self.size")
    
    if size != len(self.keys):
      raise AssertionError("size != len(self.keys)")
