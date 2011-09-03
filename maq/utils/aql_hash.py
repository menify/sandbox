
class Hash (object):
  
  __slots__ = ('values', 'size')
  
  def   __init__(self):
    
    self.values = {}
    self.size = 0
  
  #//-------------------------------------------------------//
  
  def   find(self, item):
    values = self.values.get( hash(item), [] )
    try:
      return values[ values.index( item ) ]
    except ValueError:
      return None
  
  #//-------------------------------------------------------//
  
  def   add(self, item):
    values = self.values.setdefault( hash(item), [] )
    try:
      values[ values.index( item ) ] = item
    
    except ValueError:
      values.append( item )
      self.size += 1
  
  #//-------------------------------------------------------//
  
  def   remove(self, item):
    values = self.values.get( hash(item), [] )
    try:
      del values[ values.index( item ) ]
      self.size -= 1
    
    except ValueError:
      pass
  
  #//-------------------------------------------------------//
  
  def   __contains__(self, item):
    return self.find( item ) is not None
  
  #//-------------------------------------------------------//
  
  def   __iter__(self):
    for values in self.values.values():
      for item in values:
        yield item
  
  #//-------------------------------------------------------//
  
  def   clear(self):
    self.values.clear()
    self.size = 0
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return self.size
  
  #//-------------------------------------------------------//
  
  def   __bool__(self):
    return self.size > 0
