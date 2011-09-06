class Hash (object):
  
  __slots__ = ('values', 'size', 'seq_num', 'keys')
  
  def   __init__(self):
    
    self.values = {}
    self.size = 0
    self.seq_num = 0
    self.keys = {}
  
  #//-------------------------------------------------------//
  
  def   find(self, item):
    values = self.values.get( hash(item), [] )
    for value_item, key in values:
      if value_item == item:
        return value_item, key
    
    return None, -1
  
  #//-------------------------------------------------------//
  
  def   findByKey(self, key):
    try:
      return self.keys[ key ]
    except KeyError:
      return None
  
  #//-------------------------------------------------------//
  
  def   add(self, item):
    values = self.values.setdefault( hash(item), [] )
    
    for value_item, key in values:
      if value_item == item:
        return value_item, key
    
    key = self.seq_num
    self.seq_num += 1
    
    value = (item, key )
    
    values.append( value )
    self.size += 1
    
    self.keys[ key ] = item
    
    return value
  
  #//-------------------------------------------------------//
  
  def   remove(self, item):
    values = self.values.get( hash(item), [] )
    for value_item, key in values:
      if value_item == item:
        del values[ item ]
        del self.keys[ key ]
  
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
