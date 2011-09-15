import struct

from aql_hash import Hash

class ValueManager (object):
  
  __slots__ = ('item_locations', 'hash', 'stream')
  
  #//-------------------------------------------------------//
  
  def   __init__( self, stream ):
    
    self.hash = Hash()
    self.value_locations = {}
    self.size = 0
    self.stream = stream
    self.prefix_format = ">L"   # big-endian 4 bytes
    self.prefix_size = struct.calcsize( self.prefix_format )
  
  #//-------------------------------------------------------//
  
  def   add( self, value ):
    
    value, key = self.hash.add( value )
    return value
  
  #//-------------------------------------------------------//
  
  def   newChunkSize( self, data_size ):
    return data_size * 1.5 + self.prefix_size
  
  #//-------------------------------------------------------//
  
  def   __writeData( self, offset, data )
    size_data = struct.pack( self.prefix_format, len(data) )
    stream = self.stream
    stream.seek( offset )
    stream.write( size_data )
    stream.write( data )
  
  #//-------------------------------------------------------//
  
  #//-------------------------------------------------------//
  
  def   __extendLocations( self, start_offset, extend_size ):
    for key, location in self.value_locations.items():
      if location[0] > start_offset:
        self.value_locations[ key ] = [ location[0] + extend_size, location[1] ]
  
  #//-------------------------------------------------------//
  
  def   __moveData( self, src_offset, dst_offset, size ):
    stream = self.stream
    stream.seek( src_offset )
    data = stream.read( size )
    stream.seek( dst_offset )
    stream.write( data )

  #//-------------------------------------------------------//
  
  def   __extend(self, location, data_size ):
    chuck_offset, chunk_size = location
    
    if chunk_size < (data_size + self.prefix_size):
      new_chunk_size = self.newChunkSize( data_size )
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
  
  def   saveValue( self, value, key ):
    data = pickle.dumps( ( key, value ), protocol = pickle.HIGHEST_PROTOCOL )
    data = pickletools.optimize( data )
    
    data_size = len(data)
    
    location = self.value_locations.setdefault( key, [-1,0 ] )
    chuck_offset, chunk_size = location
    if chunk_offset == -1:
      chunk_size = self.newChunkSize( data_size )
      chunk_offset = self.size
      self.size += chunk_size
      location[:] = [ chunk_offset, chunk_size ]
    
    self.__extend( location, data_size )
    
    self.__writeData( chuck_offset, data )
    
  
  #//-------------------------------------------------------//
  
  def   save( self ):
    for value, key in self.hash:
      data = pickle.dumps( ( key, value ), protocol = pickle.HIGHEST_PROTOCOL )
      data = pickletools.optimize( data )
      
      data_size = len(data)
      

    
