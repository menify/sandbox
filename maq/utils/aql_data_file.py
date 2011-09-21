import os
import struct

class DataFile (object):
  
  __slots__ = ('locations', 'file_size', 'stream', 'header_struct', 'header_size' )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    
    self.locations = []
    self.file_size = 0
    self.header_struct = struct.Struct(">LL") # big-endian 4 + 4 bytes
    self.header_size = self.header_struct.size
    
    self.__load( filename )
  
  #//-------------------------------------------------------//
  
  def   close(self):
    self.stream.close()
  
  #//-------------------------------------------------------//
  
  def   __del__(self):
    self.stream.close()
  
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
    self.stream.write( data )
  
  #//-------------------------------------------------------//
  
  def  __load( self, filename ):
    if os.path.isfile( filename ):
      self.stream = open( filename, 'r+b', 0 )
    else:
      self.stream = open( filename, 'w+b', 0 )
    
    self.file_size = self.stream.seek( 0, os.SEEK_END )
    self.stream.seek( 0 )
    
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
  
  def   __chunkData( self, data, reserved_data_size = None ):
    data_size = len(data)
    
    if reserved_data_size is None:
      reserved_data_size = max( 16, data_size + data_size // 2 )
    
    header = self.header_struct.pack( reserved_data_size, data_size )
    
    return reserved_data_size, header + data
  
  #//-------------------------------------------------------//
  
  def   __moveLocations( self, start_offset, shift_size ):
    for location in self.locations:
      if location[0] > start_offset:
        location[0] += shift_size
  
  #//-------------------------------------------------------//
  
  def   __moveBack( self, offset, reserved_data_size, chunk, new_reserved_data_size ):
    shift_size = self.header_size + reserved_data_size
    #~ print("shift_size: %s" % shift_size )
    rest_offset = offset + shift_size
    rest_data_size = self.file_size - rest_offset
    
    #~ print("rest_offset: %s" % rest_offset )
    #~ print("rest_data_size: %s" % rest_data_size )
    
    rest_chunks = self.__readBytes( rest_offset, rest_data_size )
    rest_chunks = rest_chunks + bytearray( rest_data_size - len(rest_chunks) )
    
    if chunk is None:
      chunk = bytearray()
      new_reserved_data_size = 0
    
    self.__writeBytes( offset, rest_chunks + chunk )
    
    self.__moveLocations( offset, -shift_size )
    
    self.file_size = offset + rest_data_size + new_reserved_data_size
    
    new_offset = offset + rest_data_size
    return new_offset
  
  #//-------------------------------------------------------//
  
  def   __getitem__(self, key ):
    offset, reserved_data_size, data_size = self.locations[ key ]
    return self.__readData( offset, data_size )
  
  #//-------------------------------------------------------//
  
  def   __setitem__(self, key, data ):
    
    location = self.locations[ key ]
    
    #~ print("location: %s" % location )
    
    offset, reserved_data_size, data_size = location
    new_data_size = len(data)
    
    #~ print("new_data_size: %s" % new_data_size )
    
    if new_data_size <= reserved_data_size:
      reserved_data_size, chunk = self.__chunkData( data, reserved_data_size )
      
      self.__writeBytes( offset, chunk )
      
      location[2] = new_data_size
      
    else:
      new_reserved_data_size, chunk = self.__chunkData( data )
      #~ print("new_reserved_data_size: %s" % new_reserved_data_size )
      new_offset = self.__moveBack( offset, reserved_data_size, chunk, new_reserved_data_size )
      #~ print("new_offset: %s" % new_offset )
      
      location[:] = [ new_offset, new_reserved_data_size, new_data_size ]
      #~ print("new location: %s" % location )
  
  #//-------------------------------------------------------//
  
  def   __delitem__(self, key):
    offset, reserved_data_size, data_size = self.locations[ key ]
    self.__moveBack( offset, reserved_data_size, None, 0 )
    
    del self.locations[ key ]
    
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return len( self.locations )
  
  #//-------------------------------------------------------//
  
  def   __nonzero__(self):
    return self.locations.__nonzero__()
  
  #//-------------------------------------------------------//
  
  def   __iter__(self):
    for offset, reserved_data_size, data_size in self.locations:
      yield self.__readData( offset, data_size )
  
  #//-------------------------------------------------------//
  
  def append( self, data ):
    reserved_data_size, chunk = self.__chunkData( data )
    
    offset = self.file_size
    self.__writeBytes( offset, chunk )
    
    self.file_size += reserved_data_size + self.header_size
    
    location = [ offset, reserved_data_size, len(data) ]
    #~ print("location: %s" % location )
    #~ print("file_size: %s" % self.file_size )
    #~ print("real file_size: %s" % self.stream.tell() )
    self.locations.append( location )
