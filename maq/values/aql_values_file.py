
import pickle
import pickletools

from aql_hash import Hash
from aql_data_file import DataFile

class ValuesFile (object):
  
  __slots__ = ('data_file', 'hash', 'locations' )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    self.hash = Hash()
    self.locations = {}
  
  #//-------------------------------------------------------//
  
  def   __load( self, filename )
    self.data_file = DataFile( filename )
    
    index = 0
    for data in self.data_file:
      key, value = pickle.loads( data )
      self.locations[ key ] = index
      self.hash[ key ] = value
      
      index += 1
  
  #//-------------------------------------------------------//
  
  def   __packValue( self, )
  
  #//-------------------------------------------------------//
  
  def   find(self, value ):
    return self.hash.find( value )[1]
  
  #//-------------------------------------------------------//
  
  def   add( self, value ):
    
    added_value, key = self.hash.add( value )
    if added_value is value:
      return value
    
    self.data_file.append( )
    
    return added_value
  
  #//-------------------------------------------------------//
  
  def   update( self, value ):
    
  
  #//-------------------------------------------------------//
  
  def   remove(self, value):
  
  #//-------------------------------------------------------//
  
  def   __contains__(self, value):
    return self.find( value ) is not None
  
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

    
