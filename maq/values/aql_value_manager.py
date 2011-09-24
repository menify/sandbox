
import struct

from aql_hash import Hash
from aql_data_file import DataFile

class ValueManager (object):
  
  __slots__ = ('data_file', 'hash')
  
  #//-------------------------------------------------------//
  
  def   __init__( self, stream ):
    
    self.hash = Hash()
    self.value_locations = {}
    self.size = 0
    self.stream = stream
    self.chunk_struct = struct.Struct(">LL") # big-endian 4 + 4 bytes
    self.reserved_data_size_mul = 1.5
  
  #//-------------------------------------------------------//
  
  def   __chunkData( self, data, reserved_data_size = None )
    data_size = len(data)
    
    if reserved_data_size is None:
      reserved_data_size = data_size + data_size // 2
    
    elif reserved_data_size < data_size:
      raise AssertionError( "Invalid file format")
    
    chunk_header = self.chunk_struct.pack( reserved_data_size, data_size )
    return chunk_header + data, reserved_data_size
  
  #//-------------------------------------------------------//
  
  def   __writeChunk( self, offset, data, reserved_data_size = None)
    chunk_data, reserved_data_size = self.__chunkData( data, reserved_data_size )
    self.stream.seek( offeset )
    self.stream.write( chunk_data )
    return reserved_data_size
  
  #//-------------------------------------------------------//
  
  def   __readChunk( self )
    chunk_header = self.stream.read( self.chunk_struct.size )
    reserved_data_size, data_size = self.chunk_struct.unpack( chunk_header )
    if reserved_data_size < data_size:
      raise AssertionError( "Invalid file format")
    
    data = self.stream.read( data_size )
    self.stream.seek( reserved_data_size - data_size, os.SEEK_CUR )
    
    return data, reserved_data_size
  
  #//-------------------------------------------------------//
  
  def   __resizeChunk( self, chunk_offset, reserved_data_size, data ):
    
    chunk_data, new_reserved_data_size = self.__chunkData( data )
    
    stream = self.stream
    
    next_chunk_offset = chuck_offset + reserved_data_size + self.chunk_struct.size
    rest_data_size = stream.seek( 0, os.SEEK_END ) - next_chunk_offset
    
    stream.seek( next_chunk_offset )
    rest_data = stream.read( rest_data_size )
    
    stream.seek( chuck_offset )
    stream.write( rest_data + chunk )
    
    return new_reserved_data_size
  
  #//-------------------------------------------------------//
  
  def   __extendLocations( self, start_offset, extend_size ):
    for key, location in self.value_locations.items():
      if location[0] > start_offset:
        self.value_locations[ key ] = [ location[0] + extend_size, location[1] ]
  
  #//-------------------------------------------------------//
  
  def   __extend(self, location, data_size ):
    chuck_offset, chunk_size = location
    
    if chunk_size < (data_size + self.prefix_size):
      new_chunk_size = self.__newChunkSize( data_size )
      chunk_size_delta = new_chunk_size - chunk_size
      
      next_chunk_offset = chuck_offset + chunk_size
      new_next_chunk_offset = next_chunk_offset + chunk_size_delta
      
      rest_data_size = self.size - next_chunk_offset
      
      self.size += chunk_size_delta
      
      location[1] = new_chunk_size
      
      if rest_data_size > 0:
        self.__moveData( next_chunk_offset, new_next_chunk_offset, rest_data_size )
        self.__extendLocations( chuck_offset, chunk_size_delta )
  
  #//-------------------------------------------------------//
  
  def   __saveValue( self, value, key ):
    data = pickle.dumps( ( key, value ), protocol = pickle.HIGHEST_PROTOCOL )
    data = pickletools.optimize( data )
    
    data_size = len(data)
    
    location = self.value_locations.setdefault( key, [-1,0 ] )
    chuck_offset, chunk_size = location
    if chunk_offset == -1:
      chunk_size = self.__newChunkSize( data_size )
      chunk_offset = self.size
      self.size += chunk_size
      location[:] = [ chunk_offset, chunk_size ]
    
    self.__extend( location, data_size )
    
    self.__writeData( chuck_offset, data )
    
  
  #//-------------------------------------------------------//
  
  def   add( self, value ):
    
    value, key = self.hash.add( value )
    self.__saveValue( value, key )
    return value
  
  #//-------------------------------------------------------//
  
  def   save( self, values = None ):
    
    if values is None:
      for value, key in self.hash:
        self.__saveValue( value, key )
    else:
      try:
        values = iter(values)
      except TypeError:
        values = (values, )
      
      for value in values:
        self.add( value )
  
  #//-------------------------------------------------------//
  
  def   load( self, filename ):
    stream = open( filename, "r+b" )
    
