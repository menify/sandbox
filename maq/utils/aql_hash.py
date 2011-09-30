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
  
  def   __findItem( self, pairs, item ):
    index = 0
    for value_item, value_key in pairs:
      if value_item == item:
        return index
      
      index += 1
    
    return -1
    
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
    
    pairs = self.values.setdefault( hash(item), [] )
    
    index = self.__findItem( pairs, item )
    if index == -1:
      self.__addItem( pairs, item, key )
    
    else:
      old_key = pairs[index][1]
      del self.keys[ old_key ]
      pairs[ index ] = (item, key)
      self.keys[ key ] = item
  
  #//-------------------------------------------------------//
  
  def   find(self, item):
    try:
      pairs = self.values[ hash(item) ]
      index = self.__findItem( self.values.get( hash(item), [] ), item )
      if index != -1:
        return pairs[index]
    
    except KeyError:
      pass
    
    return None, None
  
  #//-------------------------------------------------------//
  
  def   add( self, item ):
    
    pairs = self.values.setdefault( hash(item), [] )
    index = self.__findItem( pairs, item )
    if index != -1:
      return pairs[index]
    
    return self.__addItem( pairs, item, self.__genKey() )
  
  #//-------------------------------------------------------//
  
  def   update( self, item ):
    self.remove( item )
    return self.add( item )
  
  #//-------------------------------------------------------//
  
  def   remove(self, item):
    
    pairs = self.values.get( hash(item), [] )
    index = self.__findItem( pairs, item )
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
