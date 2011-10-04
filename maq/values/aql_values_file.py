
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
  
  __slots__ = ('data_file', 'hash', 'locations', 'filename', 'pickler', 'unpickler', 'pickler_stream' )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    self.hash = Hash()
    self.locations = {}
    self.filename = os.path.normcase( os.path.normpath( os.path.abspath( str(filename) ) ) )
    
    self.pickler_stream = io.BytesIO()
    self.pickler = ValuePickler( self.pickler_stream, self.hash )
    self.unpickler = ValueUnpickler( self.pickler_stream )
  
  #//-------------------------------------------------------//
  
  def   __load( self, filename )
    self.data_file = DataFile( filename )
    
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
  
  def   __packValue( self, key, value ):
    buffer = self.pickler_stream
    buffer.seek(0)
    buffer.truncate(0)
    self.pickler.dump( (key, value) )
    return buffer.getvalue()
  
  #//-------------------------------------------------------//
  
  def   __unpackValue( self, data ):
    buffer = self.pickler_stream
    buffer.seek(0)
    buffer.truncate(0)
    buffer.write(data)
    key, value = self.pickler.load()
    return key, value
  
  #//-------------------------------------------------------//
  
  def   find( self, value ):
    return self.hash.find( value )[0]
  
  #//-------------------------------------------------------//
  
  def   add( self, value ):
    
    added_value, key = self.hash.add( value )
    if added_value is not None:
      return added_value
    
    data = self.__packValue( key, value )
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

    
