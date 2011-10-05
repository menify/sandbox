
import io
import pickle
import pickletools

from aql_hash import Hash
from aql_data_file import DataFile
from aql_depends_value import DependsValue
from aql_file_value import FileName

#//---------------------------------------------------------------------------//

class _PickledDependsValue (object):
  __slots__ = ('name', 'value_keys' )
  
  def   __init__(self, depends_value, values_hash ):
    
    name = depends_value.name
    value_keys = []
    
    for value in depends_value.content.values:
      key = values_hash.find( value )[0]
      if key is None:
        name = None             # ignore invalid depends value
        value_keys = None
        break
        
      value_keys.append( key )
    
    self.name = name
    self.value_keys = value_keys
  
  #//-------------------------------------------------------//
  
  def   isValid( self ):
    return (self.name is not None) and (self.value_keys is not None)
  
  #//-------------------------------------------------------//
  
  def   restore( self, values_hash ):
    if not self.isValid():
      return None
    
    values = []
    
    for value_key in self.value_keys:
      try:
        value = values_hash[ value_key ]
      except KeyError:
        return None
      
      values.append( value )
    
    return DependsValue( self.name, values )
    
  #//-------------------------------------------------------//
  
  def   __getstate__( self ):
    return { 'name': self.name, 'value_keys' : self.value_keys }
  
  #//-------------------------------------------------------//
  
  def   __setstate__( self, state ):
    self.name = state['name']
    self.value_keys = state['value_keys']

#//---------------------------------------------------------------------------//

def restoreDepends( pdv_keys, pdv_list, values_hash ):
  
    all_keys = set( pdv_keys )
    values = {}
    
    for key, pdv in zip( pdv_keys, pdv_list ):
      values[ key ] = (pdv, all_keys & set(pdv.value_keys))
    
    restored_keys = set()
    
    while True:
      
      for key, pair in list(values.items()):
        if not pair[1]:
          value = pdv.restore( values_hash )
          values_hash.add( value )
          restored_keys.add( key )
          del values[ key ]
      
      if not restored_keys:
        break
      
      for key, pair in values.items():
        values[key][1] = pair[1] - restored_keys
      
      restored_keys.clear()

#//---------------------------------------------------------------------------//

class ValuesFile (object):
  
  __slots__ = ('data_file', 'hash', 'locations', 'filename' )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    self.hash = Hash()
    self.locations = {}
    self.filename = FileName(filename)
    self.data_file = None
    
    self.__reload()
  
  #//-------------------------------------------------------//
  
  def   __packValue( self, key, value ):
    if isinstance(value, DependsValue):
      value = _PickledDependsValue(value, self.hash )
    data = pickle.dumps( (key, value), pickle.HIGHEST_PROTOCOL )
    return pickletools.optimize( data )
  
  #//-------------------------------------------------------//
  
  def   __unpackValue( self, data ):
    key, value = pickle.loads( data )
    return key, value
  
  #//-------------------------------------------------------//
  
  def   __reload( self ):
    if self.data_file is not None:
      self.data_file.close()
    
    self.data_file = DataFile( self.filename )
    self.hash.clear()
    self.locations.clear()
    
    pdv_list = []
    pdv_keys = []
    
    index = 0
    for data in self.data_file:
      key, value = self.__unpackValue( data )
      
      if isinstance( value, _PickledDependsValue ):
        if value.isValid():
          pdv_list.append( value )
          pdv_keys.append( key )
        else:
          del self.data_file[ index ]
          continue
      
      else:
        self.hash[ key ] = value
      
      self.locations[ key ] = index
      index += 1
    
    restoreDepends( pdv_keys, pdv_list, self.hash )
  
  #//-------------------------------------------------------//
  
  def   find( self, value ):
    return self.hash.find( value )[1]
  
  #//-------------------------------------------------------//
  
  def   add( self, value ):
    
    key, added_value = self.hash.add( value )
    if added_value is not None:
      return added_value
    
    data = self.__packValue( key, value )
    self.locations[ key ] = len(self.data_file)
    self.data_file.append( data )
    
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
      old_index = self.locations[ old_key ]
      del self.data_file[ old_index ]
      
      for key, index in self.locations:
        if old_index > index:
          self.locations[ key ] = index - 1
  
  #//-------------------------------------------------------//
  
  def   __contains__(self, value):
    return self.find( value ) is not None
  
  #//-------------------------------------------------------//
  
  def   __iter__(self):
    return iter(self.hash)
  
  #//-------------------------------------------------------//
  
  def   clear(self):
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

    
