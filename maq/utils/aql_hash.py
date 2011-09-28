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
  
  def   find(self, item):
    values = self.values.get( hash(item), [] )
    for value_item, key in values:
      if value_item == item:
        return value_item, key
    
    return None, None
  
  #//-------------------------------------------------------//
  
  def   __getitem__(self, key):
    return self.keys[ key ]
  
  #//-------------------------------------------------------//
  
  @staticmethod
  def   __findItem( pairs, item ):
    index = 0
    for value_item, value_key in pairs:
      if value_item == item:
        return index, value_item, value_key
    
    return -1, None, None
    
  #//-------------------------------------------------------//
  
  def   __setitem__(self, key, item ):
    
    pairs = self.values.setdefault( hash(item), [] )
    index = self.__findItem( item )[0]
    if index != -1:
        pairs[ index ] = (item, key)
        del self.keys[ value_key ]
        self.keys[ key ] = item
    
      index += 1
    
    pair = (item, key)
    
    pairs.append( pair )
    self.size += 1
    
    self.keys[ key ] = item
  
  #//-------------------------------------------------------//
  
  def   __delitem__(self, key ):
    
    item = self.keys[ key ]
    
    pairs = self.values[ hash(item) ]
    index = 0
    for value_item, value_key in pairs:
      if value_item == item:
        del pairs[ index ] = (item, key)
        del self.keys[ value_key ]
        self.keys[ key ] = item
    
      index += 1
    
    pair = (item, key)
    
    pairs.append( pair )
    self.size += 1
    
    self.keys[ key ] = item
  
  #//-------------------------------------------------------//
  
  def   add( self, item ):
    pairs = self.values.setdefault( hash(item), [] )
    
    index = 0
    for value_item, value_key in pairs:
      if value_item == item:
          return value_item, value_key
    
    key = self.__genKey()
    
    pair = (item, key)
    
    pairs.append( pair )
    self.size += 1
    
    self.keys[ key ] = item
    
    return pair
  
  #//-------------------------------------------------------//
  
  def   remove(self, item):
    values = self.values.get( hash(item), [] )
    index = 0
    for value_item, key in values:
      if value_item == item:
        del values[ index ]
        del self.keys[ key ]
        self.size -= 1
        break
      
      index += 1
  
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
