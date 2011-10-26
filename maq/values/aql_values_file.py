
import io
import pickle

from aql_logging import logWarning
from aql_hash import Hash
from aql_data_file import DataFile
from aql_depends_value import DependsValue
from aql_file_value import FileName

#//---------------------------------------------------------------------------//

@pickleable
class _PickledDependsValue (object):
  
  __slots__ = ('name', 'keys')
  
  def   __new__( cls, name, keys ):
    self = super(_PickledDependsValue,cls).__new__(cls)
    
    self.name = name
    self.keys = keys
    
    return self
  
  #//-------------------------------------------------------//
  
  def   __getnewargs__( self ):
    return (self.name, self.keys )
  
  #//-------------------------------------------------------//
  
  def   isValid( self ):
    return (self.name is not None) and (self.value_keys is not None)
  
  #//-------------------------------------------------------//
  
  def   restore( self, values_hash ):
    if not self.isValid():
      return None
    
    values = []
    
    for key in self.keys:
      try:
        value = values_hash[ key ]
      except KeyError:
        return None
      
      values.append( value )
    
    return DependsValue( self.name, values )
  

#//---------------------------------------------------------------------------//

class ValuesFile (object):
  
  __slots__ = ('data_file', 'hash', 'pickler', 'lock' )
  
  #//-------------------------------------------------------//
  
  def   __pickableValue( self, value )
    if isinstance( value, DependsValue ):
      value_keys = self.__getValuesKeys
      
      value = _PickledDependsValue( value.name, self.hash )
      if not value.isValid():
        return None
    
    return value
  
  #//-------------------------------------------------------//
  
  def   __packValue( self, value ):
    if isinstance(value, DependsValue):
      value = _PickledDependsValue( value, self.hash )
      
    return pickle.dumps( value, pickle.HIGHEST_PROTOCOL )
  
  #//-------------------------------------------------------//
  
  def   __unpackValue( self, data ):
    value = pickle.loads( data )
    return value
  
  #//-------------------------------------------------------//
  
  def __restoreDepends( self, pdv_values ):
    
    all_keys = set( pdv_values.keys() )
    
    for key in pdv_values:
      pdv_values[ key ][2] &= all_keys
    
    restored_keys = set()
    
    while True:
      for key in list(pdv_values):
        pdv, pdv_keys = pdv_values[ key ]
        if not pdv_keys:
          value = pdv.restore( self.hash )
          if value is not None:
            self.hash[ key ] = value
            self.locations[ key ] = index
            
            del pdv_values[ key ]
            restored_keys.add( key )
          
      
      if not restored_keys:
        break
      
      for key in pdv_values:
        pdv_values[ key ][2] -= restored_keys
      
      restored_keys.clear()
    
    removed_indexes += map( lambda v: v[0], pdv_values.values() )
    removed_indexes.sort( reverse = True )
    
    for index in removed_indexes:
      self.__removeIndex( index )
  
  #//-------------------------------------------------------//
  
  def   __getValueKeys( self, values ):
    value_keys = []
    
    findValue = self.hash.find
    for value in values:
      key = findValue( value )[0]
      if key is None:
        return None
      
      value_keys.append( key )
    
    return value_keys
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    self.hash = Hash()
    self.data_file = None
    
    self.open( filename )
  
  #//-------------------------------------------------------//
  
  def   open( self, filename ):
    
    self.close()
    
    self.data_file = DataFile( filename )
    
    pdv_values = {}
    
    for key, data in self.data_file:
      value = self.__unpackValue( data )
      
      if isinstance( value, _PickledDependsValue ):
        if value.isValid():
          pdv_values[ key ] = [value, set(value.value_keys)]
        else:
          del self.data_file[ key ]
      
      else:
        self.hash[ key ] = value
    
    self.__restoreDepends( pdv_values )
  
  #//-------------------------------------------------------//
  
  def   close( self ):
    if self.data_file is not None:
      self.data_file.close()
      self.data_file = None
    
    self.locations.clear()
    self.hash.clear()
  
  #//-------------------------------------------------------//
  
  def   findValue( self, value ):
    value = self.hash.find( value )[1]
    if value is not None:
      
      pick_value = self.__pickableValue( value )
      if pick_value is None:
        return None
    
    return value
    
  
  #//-------------------------------------------------------//
  
  def   addValue( self, value ):
    
    pick_value = self.__pickableValue(value)
    if pick_value is None:
      return None
    
    data = self.__packValue( value )
    
    key = self.hash.find( value )[0]
    if key is None:
      key = self.data_file.append( data )
    else:
      self.data_file[key] = data
    
    self.hash[key] = value
    
    return value
  
  #//-------------------------------------------------------//
  
  def   update( self, value ):
    key, old_key = self.hash.update( value )
    
    data = self.__packValue( key, value )
    
    if old_key is None:
      self.locations[ key ] = len(self.data_file)
      self.data_file.append( data )
    
    else:
      index = self.locations[ old_key ]
      del self.locations[ old_key ]
      self.locations[ key ] = index
      self.data_file[ index ] = data
  
  #//-------------------------------------------------------//
  
  def   remove(self, value):
    old_key = self.hash.remove( value )
    if old_key is not None:
      locations = self.locations
      old_index = locations[ old_key ]
      del self.data_file[ old_index ]
      
      for key in locations:
        index = locations[key]
        if old_index > index:
          locations[ key ] = index - 1
  
  #//-------------------------------------------------------//
  
  def   __contains__(self, value):
    return self.find( value ) is not None
  
  #//-------------------------------------------------------//
  
  def   __iter__(self):
    return iter(self.hash)
  
  #//-------------------------------------------------------//
  
  def   clear(self):
    if self.data_file is not None:
      self.data_file.clear()
    
    self.locations.clear()
    self.hash.clear()
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return len(self.hash)
  
  #//-------------------------------------------------------//
  
  def   __bool__(self):
    return bool(self.hash)
  
  #//-------------------------------------------------------//
  
  def   selfTest(self):
    if self.data_file is not None:
      self.data_file.selfTest()
    
    self.hash.selfTest()
    
    size = len(self.locations)
    
    if size != len(self.hash):
      raise AssertionError("len(self.locations) != len(self.hash)")
    
    if size != len(self.data_file):
      raise AssertionError("size != len(self.data_file)")
    
    indexes = set()
    
    for key, index in self.locations.items():
      try:
        self.hash[ key ]
      except KeyError:
        raise AssertionError("Invalid value key")
      
      if index >= size:
        raise AssertionError("index >= size")
      
      indexes.add( index )
    
    if len(indexes) != size:
      raise AssertionError("len(indexes) != size")
