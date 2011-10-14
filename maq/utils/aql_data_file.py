import io
import os
import struct
import array

class DataFile (object):
  
  __slots__ = \
  (
    'locations',
    'file_size',
    'stream',
    'header_struct',
    'header_size',
    'file_header_size',
    'file_header_struct',
    'version',
    'max_version',
    'lock',
  )
  
  #//-------------------------------------------------------//
  
  def   __readFileVersion( self ):
    
    file_header_size = self.file_header_size
    
    file_header = self.__readBytes( 0, file_header_size )
    if len(file_header) != file_header_size:
      return 0
    
    return self.file_header_struct.unpack( file_header )
  
  #//-------------------------------------------------------//
  
  def   __nextVersion( self ):
    
    file_header = self.file_header_struct.pack( self.version )
    
    self.__writeBytes( 0, file_header )
    
    if self.version < self.max_version:
      self.version += 1
    else:
      self.version = 0
  
  #//-------------------------------------------------------//
  
  def   __readHeader( self, offset ):
    stream = self.stream
    header_size = self.header_size
    
    stream.seek( offset )
    header = stream.read( header_size )
    if len(header) != header_size:
      return 0, 0
    
    version, reserved_data_size, data_size = self.header_struct.unpack( header )
    if reserved_data_size < data_size:
      raise AssertionError( "Invalid file format" )
    
    return version, reserved_data_size, data_size
  
  #//-------------------------------------------------------//
  
  def   __readData( self, offset, data_size ):
    stream = self.stream
    stream.seek( offset + self.header_size )
    return stream.read( data_size )
  
  #//-------------------------------------------------------//
  
  def   __readBytes( self, offset, data_size ):
    stream = self.stream
    stream.seek( offset )
    return stream.read( data_size )
  
  #//-------------------------------------------------------//
  
  def   __writeBytes( self, offset, data ):
    stream = self.stream
    stream.seek( offset )
    return stream.write( data )
  
  #//-------------------------------------------------------//
  
  def   __chunkData( self, data, data_size, reserved_data_size = None ):
    
    if reserved_data_size is None:
      reserved_data_size = max( 16, data_size + data_size // 2 )
    
    version = self.__nextVersion()
    
    header = self.header_struct.pack( version, reserved_data_size, data_size )
    
    chunk = bytearray(header)
    chunk += data
    
    return version, reserved_data_size, chunk
  
  #//-------------------------------------------------------//
  
  def   __moveLocations( self, start_offset, shift_size ):
    for location in self.locations:
      if location[0] > start_offset:
        location[0] += shift_size
  
  #//-------------------------------------------------------//
  
  def   __removeChunk( self, offset, reserved_data_size ):
    
    chunk_size = self.header_size + reserved_data_size
    
    rest_offset = offset + chunk_size
    rest_data_size = self.file_size - rest_offset
    
    rest_chunks = self.__readBytes( rest_offset, rest_data_size )
    
    if rest_chunks:
        written_bytes_size = self.__writeBytes( offset, rest_chunks )
    else:
      written_bytes_size = 0
    
    self.stream.truncate( offset + written_bytes_size )
    
    self.__moveLocations( offset, -chunk_size )
    
    self.file_size -= chunk_size
    
    return offset
  
  #//-------------------------------------------------------//
  
  def   __resizeChunk( self, offset, reserved_data_size, chunk, new_reserved_data_size, new_data_size ):
    
    shift_size = new_reserved_data_size - reserved_data_size
    rest_offset = offset + self.header_size + reserved_data_size
    rest_data_size = self.file_size - rest_offset
    
    rest_chunks = self.__readBytes( rest_offset, rest_data_size )
    if rest_chunks:
      chunk += bytearray( new_reserved_data_size - new_data_size )
    
    chunk += rest_chunks
    
    written_bytes_size = self.__writeBytes( offset, chunk )
    
    self.__moveLocations( offset, shift_size )
    
    self.file_size += shift_size
    
    if new_reserved_data_size < reserved_data_size:
      self.stream.truncate( offset + written_bytes_size )
    
    return offset
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    
    self.locations = []
    self.file_size = 0
    self.stream = None
    
    self.file_header_struct = struct.Struct(">L") # big-endian 4 bytes
    self.file_header_size = self.file_header_struct.size
    self.max_version = (2 ** 32) - 1
    self.version = 0
    
    self.header_struct = struct.Struct(">LLL") # big-endian 4 + 4 bytes
    self.header_size = self.header_struct.size
    
    self.open( filename )
  
  #//-------------------------------------------------------//
  
  def  open( self, filename ):
    self.close()
    
    self.locations = []
    
    if os.path.isfile( filename ):
      self.stream = io.open( filename, 'r+b', 0 )
    else:
      self.stream = io.open( filename, 'w+b', 0 )
    
    offset = 0
    
    self.version = self.__readFileVersion()
    
    while True:
      version, reserved_data_size, data_size = self.__readHeader( offset )
      if not reserved_data_size:
        break
      
      self.locations.append( [ offset, reserved_data_size, data_size, version ] )
      offset += self.header_size + reserved_data_size
    
    self.file_size = offset
  
  #//-------------------------------------------------------//
  
  def   close(self):
    if self.stream is not None:
      self.stream.close()
      self.stream = None
      
      del self.locations[:]
      self.file_size = 0
  
  #//-------------------------------------------------------//
  
  def   lock( self ):
    pass
  
  #//-------------------------------------------------------//
  
  def   unlock( self ):
    pass
  
  #//-------------------------------------------------------//
  
  def   __del__(self):
    self.unlock()
    self.close()
  
  #//-------------------------------------------------------//
  
  def   clear(self):
    if self.stream is not None:
      self.stream.seek( 0 )
      self.stream.truncate( 0 )
    
    del self.locations[:]
    self.file_size = 0
  
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
      version, reserved_data_size, chunk = self.__chunkData( data, new_data_size, reserved_data_size )
      
      self.__writeBytes( offset, chunk )
      
      location[2:3] = [new_data_size, version ]
    
    else:
      version, new_reserved_data_size, chunk = self.__chunkData( data, new_data_size )
      
      new_offset = self.__resizeChunk( offset, reserved_data_size, chunk, new_reserved_data_size, new_data_size )
      
      location[:] = [ new_offset, new_reserved_data_size, new_data_size, version ]
  
  #//-------------------------------------------------------//
  
  def   __delitem__(self, index):
    offset, reserved_data_size, data_size = self.locations[ index ]
    self.__removeChunk( offset, reserved_data_size )
    
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
    version, reserved_data_size, chunk = self.__chunkData( data, len(data) )
    
    offset = self.file_size
    self.__writeBytes( offset, chunk )
    
    self.file_size += reserved_data_size + self.header_size
    
    location = [ offset, reserved_data_size, len(data), version ]
    self.locations.append( location )
  
  #//-------------------------------------------------------//
  def   update(self):
    version = self.__readFileVersion()
  
  #//-------------------------------------------------------//
  
  def   selfTest( self ):
    file_size = 0
    
    for offset, reserved_data_size, data_size in self.locations:
      if reserved_data_size < data_size:
        raise AssertionError("reserved_data_size < data_size")
      
      file_size += self.header_size + reserved_data_size
      
    if file_size != self.file_size:
      raise AssertionError("file_size != self.file_size")
    
    if self.stream is not None:
      real_file_size = self.stream.seek( 0, os.SEEK_END )
      if self.locations:
        last_offset, last_reserved_data_size, last_data_size = self.locations[-1]
        last_data_offset = last_offset + self.header_size
        
        if real_file_size < (last_data_offset + last_data_size) or \
           real_file_size > (last_data_offset + last_reserved_data_size) :
          print("real_file_size: %s, last location: %s" % (real_file_size, self.locations[-1] ))
          raise AssertionError("real_file_size != (last_offset + self.header_size + last_data_size)")
      
      else:
        if file_size != real_file_size:
          raise AssertionError("file_size != real_file_size")
    
    prev_offset = 0
    prev_reserved_data_size = -self.header_size
    for offset, reserved_data_size, data_size in self.locations:
      if (prev_offset + prev_reserved_data_size + self.header_size) != offset:
        raise AssertionError("(prev_offset + prev_reserved_data_size + self.header_size) != offset")
      prev_offset = offset
      prev_reserved_data_size = reserved_data_size