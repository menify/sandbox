import io
import os
import struct
import array

class DataFile (object):
  
  __slots__ = ('locations', 'file_size', 'stream', 'header_struct', 'header_size' )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    
    self.locations = []
    self.file_size = 0
    self.stream = None
    self.header_struct = struct.Struct(">LL") # big-endian 4 + 4 bytes
    self.header_size = self.header_struct.size
    
    self.open( filename )
  
  #//-------------------------------------------------------//
  
  def   close(self):
    if self.stream is not None:
      self.stream.close()
      self.stream = None
      
      del self.locations[:]
      self.file_size = 0
  
  #//-------------------------------------------------------//
  
  def   __del__(self):
    self.close()
  
  #//-------------------------------------------------------//
  
  def   clear(self):
    if self.stream is not None:
      self.stream.seek( 0 )
      self.stream.truncate( 0 )
    
    del self.locations[:]
    self.file_size = 0
  
  #//-------------------------------------------------------//
  
  def   __readHeader( self ):
    header = self.stream.read( self.header_size )
    if len(header) != self.header_size:
      return 0, 0
    
    reserved_data_size, data_size = self.header_struct.unpack( header )
    if reserved_data_size < data_size:
      raise AssertionError( "Invalid file format" )
    
    return reserved_data_size, data_size
  
  #//-------------------------------------------------------//
  
  def   __readData( self, offset, data_size ):
    self.stream.seek( offset + self.header_size )
    return self.stream.read( data_size )
  
  #//-------------------------------------------------------//
  
  def   __readBytes( self, offset, data_size ):
    self.stream.seek( offset )
    return self.stream.read( data_size )
  
  #//-------------------------------------------------------//
  
  def   __writeBytes( self, offset, data ):
    self.stream.seek( offset )
    return self.stream.write( data )
  
  #//-------------------------------------------------------//
  
  def  open( self, filename ):
    self.close()
    
    self.locations = []
    
    if os.path.isfile( filename ):
      self.stream = io.open( filename, 'r+b', 0 )
    else:
      self.stream = io.open( filename, 'w+b', 0 )
    
    offset = 0
    
    while True:
      reserved_data_size, data_size = self.__readHeader()
      if not reserved_data_size:
        break
      
      self.locations.append( [ offset, reserved_data_size, data_size ] )
      offset += self.header_size + reserved_data_size
      self.stream.seek( offset )
    
    self.file_size = offset
  
  #//-------------------------------------------------------//
  
  def   __chunkData( self, data, data_size, reserved_data_size = None ):
    
    if reserved_data_size is None:
      reserved_data_size = max( 16, data_size + data_size // 2 )
    
    header = self.header_struct.pack( reserved_data_size, data_size )
    
    chunk = bytearray(header)
    chunk += data
    
    return reserved_data_size, chunk
  
  #//-------------------------------------------------------//
  
  def   __moveLocations( self, start_offset, shift_size ):
    for location in self.locations:
      if location[0] > start_offset:
        location[0] += shift_size
  
  #//-------------------------------------------------------//
  
  def   __resizeChunk( self, offset, reserved_data_size, chunk, new_reserved_data_size ):
    
    if chunk is None:
      chunk = bytearray()
      new_reserved_data_size = -self.header_size
    else:
      chunk = chunk + bytearray( new_reserved_data_size + self.header_size - len(chunk) )
    
    shift_size = new_reserved_data_size - reserved_data_size
    rest_offset = offset + self.header_size + reserved_data_size
    rest_data_size = self.file_size - rest_offset
    
    rest_chunks = self.__readBytes( rest_offset, rest_data_size )
    
    written_bytes_size = self.__writeBytes( offset, chunk + rest_chunks )
    
    self.__moveLocations( offset, shift_size )
    
    self.file_size += shift_size
    
    if new_reserved_data_size < reserved_data_size:
      self.stream.truncate( offset + written_bytes_size )
    
    return offset
  
  #//-------------------------------------------------------//
  
  def   __getitem__(self, index ):
    offset, reserved_data_size, data_size = self.locations[ index ]
    return self.__readData( offset, data_size )
  
  #//-------------------------------------------------------//
  
  def   __setitem__(self, index, data ):
    
    location = self.locations[ index ]
    
    offset, reserved_data_size, data_size = location
    new_data_size = len(data)
    
    if new_data_size <= reserved_data_size:
      reserved_data_size, chunk = self.__chunkData( data, new_data_size, reserved_data_size )
      
      self.__writeBytes( offset, chunk )
      
      location[2] = new_data_size
    
    else:
      new_reserved_data_size, chunk = self.__chunkData( data, new_data_size )
      
      new_offset = self.__resizeChunk( offset, reserved_data_size, chunk, new_reserved_data_size )
      
      location[:] = [ new_offset, new_reserved_data_size, new_data_size ]
  
  #//-------------------------------------------------------//
  
  def   __delitem__(self, index):
    offset, reserved_data_size, data_size = self.locations[ index ]
    self.__resizeChunk( offset, reserved_data_size, None, 0 )
    
    del self.locations[ index ]
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return len( self.locations )
  
  #//-------------------------------------------------------//
  
  def   __bool__(self):
    return bool(self.locations)
  
  #//-------------------------------------------------------//
  
  def   __iter__(self):
    for offset, reserved_data_size, data_size in self.locations:
      yield self.__readData( offset, data_size )
  
  #//-------------------------------------------------------//
  
  def append( self, data ):
    reserved_data_size, chunk = self.__chunkData( data, len(data) )
    
    offset = self.file_size
    self.__writeBytes( offset, chunk )
    
    self.file_size += reserved_data_size + self.header_size
    
    location = [ offset, reserved_data_size, len(data) ]
    self.locations.append( location )
  
  #//-------------------------------------------------------//
  
  def   selfTest( self ):
    file_size = 0
    
    sorted_locations = []
    
    for offset, reserved_data_size, data_size in self.locations:
      if reserved_data_size < data_size:
        raise AssertionError("reserved_data_size < data_size")
      
      sorted_locations.append( (offset, reserved_data_size, data_size) )
      file_size += self.header_size + reserved_data_size
      
    if file_size != self.file_size:
      raise AssertionError("file_size != self.file_size")
    
    sorted_locations.sort()
    
    if self.stream is not None:
      real_file_size = self.stream.seek( 0, os.SEEK_END )
      if sorted_locations:
        last_offset, last_reserved_data_size, last_data_size = sorted_locations[-1]
      
        if (file_size < real_file_size) or (real_file_size < (last_offset + last_data_size)):
          print("file_size: %s, real_file_size: %s, last_offset: %s, last_data_size: %s" % (file_size, real_file_size, last_offset, last_data_size))
          raise AssertionError("(file_size < real_file_size) or (real_file_size < (last_offset + last_data_size)")
      
      else:
        if file_size != real_file_size:
          raise AssertionError("file_size != real_file_size")
    
    prev_offset = 0
    prev_reserved_data_size = -self.header_size
    for offset, reserved_data_size, data_size in sorted_locations:
      if (prev_offset + prev_reserved_data_size + self.header_size) > offset:
        raise AssertionError("(prev_offset + prev_reserved_data_size + self.header_size) > offset")
      prev_offset = offset
      prev_reserved_data_size = reserved_data_size
