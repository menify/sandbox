
import io
import pickle

from aql_logging import logWarning
from aql_xash import Xash
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
  
  def   restore( self, xash ):
    if not self.isValid():
      return None
    
    values = []
    
    for key in self.keys:
      try:
        value = xash[ key ]
      except KeyError:
        return None
      
      values.append( value )
    
    return DependsValue( self.name, values )

#//---------------------------------------------------------------------------//

class ValuesFile (object):
  
  __slots__ = ('data_file', 'xash', 'pickler', 'lock' )
  
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
          value = pdv.restore( self.xash )
          if value is not None:
            self.xash[ key ] = value
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
    
    findValue = self.xash.find
    for value in values:
      key = findValue( value )[0]
      if key is None:
        return None
      
      value_keys.append( key )
    
    return value_keys
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    self.xash = Xash()
    self.data_file = None
    self.pickler = ValuePickler()
    self.open( filename )
  
  #//-------------------------------------------------------//
  
  def   open( self, filename ):
    
    lock = FileLock( filename )
    
    self.lock = lock
    
    with lock.readLock():
      self.data_file = DataFile( filename )
      
      dep_values = {}
      loads = self.pickler.loads
      
      for key, data in self.data_file:
        value = loads( data )
        
        if isinstance( value, _PickledDependsValue ):
          if value.isValid():
            dep_values[ key ] = [value, set(value.value_keys)]
          else:
            del self.data_file[ key ]
        
        else:
          self.xash[ key ] = value
      
      self.__restoreDepends( dep_values )
  
  #//-------------------------------------------------------//
  
  def   update( self ):
    
    xash = self.xash
    data_file = self.data_file
    loads = self.pickler.loads
    
    added_keys, deleted_keys = self.data_file.update()
    dep_values = {}
    
    for key in added_keys:
      value = loads( data_file[key] )
      
      if isinstance( value, _PickledDependsValue ):
        if value.isValid():
          dep_values[ key ] = [value, set(value.value_keys)]
        else:
          del self.data_file[ key ]
      
      else:
        self.xash[ key ] = value
    
    for key in deleted_keys:
      
      try:
        del xash[ key ]
        self.__removeDepends( key )
      except KeyError:
        pass
      
    self.__restoreDepends( dep_values )
  
  #//-------------------------------------------------------//
  
  def   close( self ):
    if self.data_file is not None:
      self.data_file.close()
      self.data_file = None
    
    self.locations.clear()
    self.xash.clear()
  
  #//-------------------------------------------------------//
  
  def   findValue( self, value ):
    value = self.xash.find( value )[1]
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
    
    key = self.xash.find( value )[0]
    if key is None:
      key = self.data_file.append( data )
    else:
      self.data_file[key] = data
    
    self.xash[key] = value
    
    return value
  
  #//-------------------------------------------------------//
  
  def   update( self, value ):
    key, old_key = self.xash.update( value )
    
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
    old_key = self.xash.remove( value )
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
    return iter(self.xash)
  
  #//-------------------------------------------------------//
  
  def   clear(self):
    if self.data_file is not None:
      self.data_file.clear()
    
    self.locations.clear()
    self.xash.clear()
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return len(self.xash)
  
  #//-------------------------------------------------------//
  
  def   __bool__(self):
    return bool(self.xash)
  
  #//-------------------------------------------------------//
  
  def   selfTest(self):
    if self.data_file is not None:
      self.data_file.selfTest()
    
    self.xash.selfTest()
    
    size = len(self.locations)
    
    if size != len(self.xash):
      raise AssertionError("len(self.locations) != len(self.xash)")
    
    if size != len(self.data_file):
      raise AssertionError("size != len(self.data_file)")
    
    indexes = set()
    
    for key, index in self.locations.items():
      try:
        self.xash[ key ]
      except KeyError:
        raise AssertionError("Invalid value key")
      
      if index >= size:
        raise AssertionError("index >= size")
      
      indexes.add( index )
    
    if len(indexes) != size:
      raise AssertionError("len(indexes) != size")
