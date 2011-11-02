
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
    return ( self.name, self.keys )
  
  #//-------------------------------------------------------//
  
  def   restore( self, xash ):
    values = []
    
    try:
      for key in self.keys:
        values.append( xash[ key ] )
    except TypeError:
      values = None
    except KeyError:
      values = None
    
    return DependsValue( self.name, values )

#//---------------------------------------------------------------------------//

class ValuesFile (object):
  
  __slots__ = ('data_file', 'xash', 'pickler', 'lock' , 'deps', 'loads', 'dumps')
  
  #//-------------------------------------------------------//
  
  def   __addDeps( self, key, dep_keys ):
    deps_Setdefault = self.deps.setdefault
    for dep_key in dep_keys:
      deps_Setdefault( dep_key, set() ).add( key )
  
  #//-------------------------------------------------------//
  
  def   __addValue( self, key, value )
    
    old_key, val = self.xash.find( value )
    if val is not None:
      if value.content != val.content:
        if isinstance(value, DependsValue):
          data = self.dumps( _PickledDependsValue( value.name, value.content ) )
          
        data = self.dumps( value )
        self.data_file.replace( old_key, data )
    else:
      if key is None:
        key = data_file.append( data )
      
      xash[key] = value

  
  #//-------------------------------------------------------//
  def   __getValueKeys( self, values ):
  
  if isinstance(values, NoContent):
    return []
    
  value_keys = []
  
  findValue = self.xash.find
  for value in values:
    key = findValue( value )[0]
    if key is None:
      return None
    
    value_keys.append( key )
  
  return value_keys
  
  #//-------------------------------------------------------//
  
  def   __sortAddedValues( self, values ):
    
    dep_values = {}
    
    for val in values:
      if isinstance(val, DependsValue ):
        vals = getattr(val.content, 'values', None):
        if values is not None:
          dep_values[ id(val) ] = [val, set(map(id, vals))]
  
  #//-------------------------------------------------------//
  
  def __sortDepends( self, dep_values ):
    
    all_keys = set( dep_values )
    
    for key, value_keys in dep_values.items():
      value_keys[1] &= all_keys
    
    sorted_deps = []
    
    added_keys = set()
    
    while True:
      for key, value_keys in list(dep_values.items()):
        value, dep_keys = value_keys
        if not dep_keys:
          del dep_values[ key ]
          added_keys.add( key )
          sorted_deps.append( (key, value ) )
      
      if not added_keys:
        break
      
      for key, value_keys in dep_values.items():
        value_keys[1] -= added_keys
      
      added_keys.clear()
    
    for key, value_keys in dep_values.items():
      value = value_keys[0]
      value.content = NoContent()
      sorted_deps.append( (key, value) )
    
    return sorted_deps
  
  #//-------------------------------------------------------//
  
  def __restoreDepends( self, dep_values ):
    
    sorted_deps = self.__sortDepends( dep_values )
    
    xash = self.xash
    
    for key, pick_dep_value in sorted_deps:
      dep_value = pick_dep_value.restore( xash )
      
      self.__addValue( key, dep_value )
      xash[ key ] = dep_value
      if not isinstance(dep_value.values, NoContent):
        self.__addDeps( key, value.keys )

    
    all_keys = set( dep_values )
    
    for key, value_keys in dep_values.items():
      value_keys[1] &= all_keys
    
    restored_keys = set()
    
    xash = self.xash
    
    while True:
      for key, value_keys in list(dep_values.items()):
        value, dep_keys = value_keys
        if not dep_keys:
          dep_value = value.restore( xash )
          xash[ key ] = dep_value
          if not isinstance(dep_value.values, NoContent):
            self.__addDeps( key, value.keys )
          
          del dep_values[ key ]
          restored_keys.add( key )
      
      if not restored_keys:
        break
      
      for key, value_keys in dep_values.items():
        value_keys[1] -= restored_keys
      
      restored_keys.clear()
    
    for key, value_keys in dep_values.items():
      value = value_keys[0]
      xash[ key ] = DependsValue( value.name, None )
  
  #//-------------------------------------------------------//
  
  def __invalidateDepends( self, deleted_keys ):
    
    xash = self.xash
    data_file = self.data_file
    dumps = self.pickler.dumps
    
    for key in deleted_keys:
      
      try:
        del xash[ key ]
        for dep_key in self.deps[key]:
          dep_value = xash[ dep_key ]
          dep_value.content = NoContent
          data = dumps( _PickledDependsValue( dep_value.name, NoContent ) )
          data_file[ dep_key ] = data
          
      except KeyError:
        pass
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    self.xash = Xash()
    self.deps = {}
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
          dep_values[ key ] = [value, set(value.value_keys)]
        
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
          dep_values[ key ] = [value, set(value.value_keys)]
      
      else:
        xash[ key ] = value
    
    self.__restoreDepends( dep_values )
    
    self.__invalidateDepends( deleted_keys )
  
  #//-------------------------------------------------------//
  
  def   close( self ):
    if self.data_file is not None:
      self.data_file.close()
      self.data_file = None
    
    self.locations.clear()
    self.xash.clear()
  
  #//-------------------------------------------------------//
  
  def   findValues( self, values ):
    
    with self.lock.readLock():
      self.update()
    
    out_values = []
    
    xash = self.xash
    for value in values:
      val = xash.find( value )[1]
      if val is None:
        val = type(value)( value.name, None )
      
      out_values.append( val )
    
    return out_values
  
  #//-------------------------------------------------------//
  
  def   addValues( self, values ):
    
    with self.lock.writeLock():
      self.update()
      
      data_file = self.data_file
      xash = self.xash
      
      for value in values:
        key, val = xash.find( value )
        if val is not None:
          if value.content != val.content:
            data_file.replace( key, data )
        else:
          key = data_file.append( data )
          xash[key] = value
  
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
  
  def   clear(self):
    with self.lock.writeLock():
      if self.data_file is not None:
        self.data_file.clear()
    
    self.locations.clear()
    self.xash.clear()
  
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
