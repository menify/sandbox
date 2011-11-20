
import io
import pickle

from aql_logging import logWarning
from aql_xash import Xash
from aql_data_file import DataFile
from aql_depends_value import DependsValue
from aql_file_value import FileName

#//---------------------------------------------------------------------------//

DependsKeysContent = tuple

#//---------------------------------------------------------------------------//

def _sortDepends( dep_sort_data ):
  
  all_keys = set( dep_sort_data )
  
  for key, value_keys in dep_sort_data.items():
    value_keys[1] &= all_keys
  
  sorted_deps = []
  
  added_keys = set()
  
  while True:
    for key, value_keys in list(dep_sort_data.items()):
      value, dep_keys = value_keys
      if not dep_keys:
        del dep_sort_data[ key ]
        added_keys.add( key )
        sorted_deps.append( (key, value ) )
    
    if not added_keys:
      break
    
    for key, value_keys in dep_sort_data.items():
      value_keys[1] -= added_keys
    
    added_keys.clear()
  
  for key, value_keys in dep_values.items():
    value = value_keys[0]
    value = DependsValue( value.name, None )
    sorted_deps.append( (key, value) )
  
  return sorted_deps

#//---------------------------------------------------------------------------//

class DependsKeys (object):
  __slots__ = ('values', 'deps')
  
  #//-------------------------------------------------------//
  
  def   __init__(self):
    values = {}
    deps = {}
  
  #//-------------------------------------------------------//
  
  def   __setitem__(self, dep_key, value_keys ):
    self.deps[ dep_key ] = keys
    values_setdefault = self.values.setdefault
    for value_key in value_keys:
      values_setdefault( value_key , set() ).add( dep_key )
  
  #//-------------------------------------------------------//
  
  def   __getitem__(self, dep_key ):
    return self.deps[ dep_key ]
  
  #//-------------------------------------------------------//
  
  def   clear(self):
    self.deps.clear()
    self.values.clear()
  
  #//-------------------------------------------------------//
  
  def   remove( self, key ):
    
    removed_deps = set()
    removing_keys = set([key])
    
    values = self.values
    values_pop = values.pop
    deps_pop = self.deps.pop
    
    while removing_keys:
      key = removing_keys.pop()
      
      try:
        value_keys = deps_pop( key )
        removed_deps.add( key )
        
        for value_key in value_keys:
          try:
            values[value_key].remove( key )
          except KeyError:
            pass
        
      except KeyError:
        pass
      
      try:
        removing_keys += values_pop( key )
      except KeyError:
        pass
    
    return removed_deps
  
#//---------------------------------------------------------------------------//

class ValuesFile (object):
  
  __slots__ = ('data_file', 'xash', 'pickler', 'lock' , 'deps', 'loads', 'dumps')
  
  #//-------------------------------------------------------//
  
  def   __getKeysOfValues( self, values ):
  
  value_keys = set()
  value_keys_append = value_keys.add
  
  findValue = self.xash.find
  try:
    for value in values:
      key = findValue( value )[0]
      if key is None:
        return None
      
      value_keys_append( key )
  
  except TypeError:
    return None
  
  return value_keys
  
  #//-------------------------------------------------------//
  
  def   __getValuesByKeys( self, keys ):
  
  values = []
  values_append = values.append
  
  getValue = self.xash.__getitem__
  
  try:
    for key in keys
      values_append( getValue( key ) )
  except KeyError:
    return None
  except TypeError:
    return None
  
  return values
  
  #//-------------------------------------------------------//
  
  def   __sortValues( self, values ):
    
    sorted_values = []
    
    dep_values = {}
    
    for value in values:
      if isinstance(value, DependsValue ):
        try:
          dep_values[ id(value) ] = [value, set(map(id, value.content))]
        except TypeError:
          sorted_values.append( value )
      else:
        sorted_values.append( value )
    
    return sorted_values, _sortDepends( dep_values )
  
  #//-------------------------------------------------------//
  
  def __restoreDepends( self, dep_values ):
    
    sorted_deps = _sortDepends( dep_values )
    
    xash = self.xash
    
    for key, dep_keys_value in sorted_deps:
      values = self.__getValuesByKeys( dep_keys_value.content )
      dep_value = DependsValue( dep_keys_value.name, values )
      
      xash[ key ] = dep_value
      if values is not None:
        self.deps[ key ] = value_keys
  
  #//-------------------------------------------------------//
  
  def   __removedDepends( self, removed_deps ):
    if removed_keys:
      xash = self.xash
      replace = self.data_file.replace
      dumps = self.dumps
      
      for removed_key in removed_keys:
        dep_value = xash.pop( removed_key )
        dep_value = DependsValue( dep_value.name, None )
        new_key = replace( removed_key, dumps( dep_value ) )
        xash[ new_key ] = dep_value
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    self.xash = Xash()
    self.deps = DependsKeys()
    self.data_file = None
    self.pickler = ValuePickler()
    self.open( filename )
    self.loads = self.pickler.loads
    self.dumps = self.pickler.dumps
  
  #//-------------------------------------------------------//
  
  def   __loadValue( self, key, data, dep_values ):
    
    value = self.loads( data )
    
    if isinstance( value, DependsValue ):
      try:
        dep_values[ key ] = [value, set(value.content)]
      except TypeError:
        self.xash[ key ] = value
    else:
      self.xash[ key ] = value
  
  #//-------------------------------------------------------//
  
  def   open( self, filename ):
    
    lock = FileLock( filename )
    self.lock = lock
    
    with lock.readLock():
      self.data_file = DataFile( filename )
      
      dep_values = {}
      for key, data in self.data_file:
        self.__loadValue( key, data, dep_values )
      
      self.__restoreDepends( dep_values )
  
  #//-------------------------------------------------------//
  
  def   __update( self ):
    
    xash = self.xash
    data_file = self.data_file
    loads = self.pickler.loads
    
    added_keys, deleted_keys = data_file.update()
    
    #//-------------------------------------------------------//
    
    removed_keys = set()
    deps_remove = self.deps.remove
    for del_key in deleted_keys:
      del xash[ del_key ]
      removed_keys += deps_remove( del_key )
    
    removed_keys -= deleted_keys
    
    if removed_keys:
      logWarning("DataFile is unsynchronized")
      self.__removedDepends( removed_keys )
    
    #//-------------------------------------------------------//
    
    dep_values = {}
    
    for key in added_keys:
      self.__loadValue( key, data_file[key], dep_values )
    
    self.__restoreDepends( dep_values )
  
  #//-------------------------------------------------------//
  
  def   close( self ):
    if self.data_file is not None:
      self.data_file.close()
      self.data_file = None
    
    self.locations.clear()
    self.xash.clear()
  
  #//-------------------------------------------------------//
  
  def   findValues( self, values ):
    
    with self.lock.writeLock():
      self.__update()
    
    out_values = []
    
    xash = self.xash
    for value in values:
      val = xash.find( value )[1]
      if val is None:
        val = type(value)( value.name, None )
      
      out_values.append( val )
    
    return out_values
  
  #//-------------------------------------------------------//
  
  def   __addValue( self, value ):
    key, val = xash.find( value )
    if val is not None:
      if value.content != val.content:
        new_key = data_file.replace( key, self.dumps( value ) )
        xash[ new_key ] = value
        
        removed_keys = deps.remove( key )
        self.__removedDepends( removed_keys )
    else:
      key = data_file.append( self.dumps( value ) )
      xash[key] = value
  
  #//-------------------------------------------------------//
  
  def   __addDepValue( self, value ):
    
    deps = self.deps
    dep_value = DependsValue( value.name, self.__getKeysOfValues( value.content ) )
    
    key, val = xash.find( value )
    if val is not None:
      if deps[ key ] != dep_value.content:
        data = self.dumps( dep_value )
        
        new_key = self.data_file.replace( key, data )
        xash[ new_key ] = dep_value
        
        removed_keys = deps.remove( key )
        self.__removedDepends( removed_keys )
        
        deps[ key ] = content_keys
        
    else:
      data = self.dumps( dep_value )
      key = self.data_file.append( data )
      xash[key] = value
      deps[ key ] = content_keys
  
  #//-------------------------------------------------------//
  
  def   addValues( self, values ):
    
    values, dep_values = self.__sortValues( values )
    
    with self.lock.writeLock():
      self.__update()
      
      for value in values:
        self.__addValue( value )
      
      for dep_value in dep_values:
        self.__addDepValue( dep_value )
  
  #//-------------------------------------------------------//
  
  def   clear(self):
    with self.lock.writeLock():
      if self.data_file is not None:
        self.data_file.clear()
    
    self.xash.clear()
    self.deps.clear()
  
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
