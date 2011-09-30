import uuid

class Hash (object):
  
  __slots__ = ('values', 'size', 'seq_num', 'keys')
  
  def   __init__(self):
    
    self.values = {}
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
    pairs = self.values.setdefault( hash(item), [] )
    
    index = 0
    for value_item, value_key in pairs:
      if value_item == item:
        return pairs, index
      
      index += 1
    
    return pairs, -1
    
  #//-------------------------------------------------------//
  
  def   __addItem( self, pairs, item, key ):
    pair = (item, key)
    
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
  
  def   __updateItem( self, pairs, index, item, key ):
    
    pair = (item, key)
    old_key = pairs[index][1]
    del self.keys[ old_key ]
    pairs[ index ] = pair
    self.keys[ key ] = item
    
    return pair
  
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
      self.__addItem( pairs, item, key )
    else:
      self.__updateItem( pairs, index, item, key )
  
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
    
    return self.__addItem( pairs, item, self.__genKey() )
  
  #//-------------------------------------------------------//
  
  def   update( self, item ):
    key = self.__genKey()
    
    pairs, index = self.__findItem( item )
    if index == -1:
      return self.__addItem( pairs, item, key )
    
    return self.__updateItem( pairs, index, item, key )
  
  #//-------------------------------------------------------//
  
  def   remove(self, item):
    
    pairs, index = self.__findItem( item )
    if index != -1:
      key = pairs[index][1]
      del self.keys[ key ]
      del pairs[ index ]
      
      self.size -= 1

  
  #//-------------------------------------------------------//
  
  def   __contains__(self, item):
    return self.find( item )[0] is not None
  
  #//-------------------------------------------------------//
  
  def   __iter__(self):
    for key, item in self.keys.items():
      yield item
  
  #//-------------------------------------------------------//
  
  def   clear(self):
    self.values.clear()
    self.keys.clear()
    self.size = 0
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return self.size
  
  #//-------------------------------------------------------//
  
  def   __bool__(self):
    return self.size > 0
