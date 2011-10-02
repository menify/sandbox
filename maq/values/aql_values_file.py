
import io
import pickle
import pickletools

from aql_hash import Hash
from aql_data_file import DataFile
from aql_depends_value import DependsValue, DependsValueContent

#//---------------------------------------------------------------------------//

class _PickledDependsValue (object):
  __slots__ = ('name', 'value_keys' )
  
  def   __init__(self, depends_value, values_hash ):
    
    name = depends_value.name
    value_keys = []
    
    for value in depends_value.content.values:
      key = values_hash.find( value )[1]
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

class ValuePickler(pickle.Pickler):

    def __init__(self, file, values_hash ):
        super().__init__(file)
        self.values_hash = values_hash
    
    def persistent_id( self, value ):
        if isinstance(value, DependsValue):
          return _PickledDependsValue( value, self.values_hash )
        else:
          return None   # value needs to be pickled as usual

#//---------------------------------------------------------------------------//

class ValueUnpickler(pickle.Unpickler):

    def persistent_load( self, pdv ):
        if isinstance( pdv, _PickledDependsValue )
          return pdv
        else:
          raise pickle.UnpicklingError("Unsupported persistent object")

#//---------------------------------------------------------------------------//

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
  
  def   __packValue( self, value, key ):
    buffer = io.BytesIO()
    
    packer = pickle.
  
  #//-------------------------------------------------------//
  
  def   find( self, value ):
    return self.hash.find( value )[0]
  
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

    
