import io
import os
import struct
import array

class   _DFLocation (object):
  __slots__ = \
  (
    'version',
    'offset',
    'capacity',
    'size',
  )
  
  max_version = (2 ** 32) - 1
  header_struct = struct.Struct(">QLLL") # big-endian, 8 bytes (key), 4 bytes (version), 4 bytes (capacity), 4 bytes (size)
  header_size = self.header_struct.size
  
  #//-------------------------------------------------------//
  
  def   __init__(self, offset ):
    
    self.version = 0
    self.offset = offset
    self.capacity = 0
    self.size = 0
  
  #//-------------------------------------------------------//
  
  @classmethod
  def  load( cls, stream, offset, header_size = header_size, header_struct = header_struct ):
    
    stream.seek( offset )
    header = stream.read( header_size )
    
    if len(header) != header_size:
      return -1, None, 0
    
    self = cls.__new__(cls)
    
    key, self.version, capacity, size = header_struct.unpack( header )
    if capacity < size:
      raise AssertionError( "Invalid file format" )
    
    self.offset = offset
    self.capacity = capacity
    self.size = size
    
    return key, self, header_size + capacity
  
  #//-------------------------------------------------------//
  
  def   pack( self, key, data, max_version = max_version, header_struct = header_struct ):
    
    if self.version < max_version:
      self.version += 1
    else:
      self.version = 0
    
    size = len(data)
    
    if self.capacity < size:
      self.capacity = size + size // 2
    
    self.size = size
    
    header = header_struct.pack( key, self.version, self.capacity, size )
    
    chunk = bytearray(header)
    chunk += data
    
    return chunk
  
  #//-------------------------------------------------------//
  
  def   data( self, stream, header_size = header_size ):
    stream.seek( self.offset + header_size )
    return stream.read( self.size )
  
  #//-------------------------------------------------------//
  
  def   chunkSize( self, header_size = header_size )
    return header_size + self.capacity
  
  #//-------------------------------------------------------//
  
  def   readTail( self, stream, header_size = header_size )
    tail_offset = self.offset + header_size + self.capacity
    stream.seek( tail_offset )
    return stream.read()

#//===========================================================================//

class _DFHeader( object ):
  
  __slots__ = \
  (
    'version',
    'uid',
  )
  
  header_struct = struct.Struct(">LQ") # big-endian, 4 bytes (file version), 8 bytes (next unique ID)
  header_size = self.file_header_struct.size
  max_version = (2 ** 32) - 1
  max_uid = (2 ** 64) - 1
  
  #//-------------------------------------------------------//
  
  def   __init__(self):
    self.version = 0
    self.uid = 0
  
  #//-------------------------------------------------------//
  
  def   load( self, stream, header_size = header_size, header_struct = header_struct ):
    stream.seek( 0 )
    header = stream.read( header_size )
    
    if len(header) != header_size:
      self.version, self.uid = 0, 0
      return True, 0
    
    version = self.version
    self.version, self.uid = header_struct.unpack( file_header )
    
    return (version != self.version), header_size
  
  #//-------------------------------------------------------//
  
  def   save( self, stream, max_version = max_version, header_struct = header_struct ):
    
    if self.version < max_version:
      self.version += 1
    else:
      self.version = 0
    
    header = header_struct.pack( self.version, self.uid )
    
    stream.seek(0)
    return stream.write( header )
  
  #//-------------------------------------------------------//
  
  def   nextKey( self, stream, max_uid = max_uid ):
    key = self.uid
    
    if key < max_uid:
      self.uid += 1
    else:
      self.uid = 0
    
    self.write( stream )
    
    return key


#//===========================================================================//

class DataFile (object):
  
  __slots__ = \
  (
    'locations',
    'file_header',
    'file_size',
    'stream',
    'lock',
  )
  
  #//-------------------------------------------------------//
  
  def   __moveLocations( self, start_offset, shift_size ):
    for location in self.locations.values():
      if location.offset > start_offset:
        location.offset += shift_size
  
  #//-------------------------------------------------------//
  
  def   __init__( self, filename ):
    
    self.locations = {}
    self.file_header = _DFHeader()
    self.file_size = 0
    self.stream = None
    
    self.open( filename )
  
  #//-------------------------------------------------------//
  
  def  open( self, filename, loadLocation = _DFLocation.load):
    self.close()
    
    if os.path.isfile( filename ):
      stream = io.open( filename, 'r+b', 0 )
    else:
      stream = io.open( filename, 'w+b', 0 )
    
    self.stream = stream
    
    offset = self.file_header.read( stream )
    if not offset:
      return
    
    stream = self.stream
    
    while True:
      key, location, size = loadLocation( stream, offset )
      if key == -1:
        break
      
      locations[key] = location
      offset += size
    
    self.file_size = offset
  
  #//-------------------------------------------------------//
  
  def   update(self, loadLocation = _DFLocation.load ):
    updated, offset = self.file_header.read( self.stream )
    if not updated:
      return [], [], []
    
    added_keys = []
    modified_keys = []
    deleted_keys = set(self.locations)
    
    locations = {}
    
    stream = self.stream
    getLocation = self.locations.__getitem__
    
    while True:
      key, location, size = loadLocation( stream, offset )
      if key == -1:
        break
      
      try:
        deleted_keys.remove( key )
        
        if getLocation(key).version != location.version:
          modified_keys.append( key )
      except KeyError:
          added_keys.append( key )
      
      locations[key] = location
      offset += size
    
    self.locations = locations
    self.file_size = offset
    
    return added_keys, modified_keys, deleted_keys
  
  #//-------------------------------------------------------//
  
  def   close(self):
    if self.stream is not None:
      self.stream.close()
      self.stream = None
      
      self.locations.clear()
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
    stream = self.stream
    if stream is not None:
      stream.seek( 0 )
      stream.truncate( 0 )
    
    del self.locations[:]
    self.file_size = 0
  
  #//-------------------------------------------------------//
  
  def append( self, data ):
    
    stream  = self.stream
    key     = self.file_header.nextKey( stream )
    offset  = self.file_size
    
    location = _DFLocation( offset )
    
    chunk = location.pack( key, data )
    
    stream.seek( offset )
    stream.write( chunk )
    
    self.file_size += location.chunkSize()
    
    self.locations[key] = location
    
    return key
  
  #//-------------------------------------------------------//
  
  def   __setitem__(self, key, data ):
    
    location = self.locations[ key ]
    capacity = location.capacity
    
    chunk = location.pack( key, data )
    
    oversize = location.capacity - capacity;
    
    stream = self.stream
    
    if oversize > 0:
      chunk += location.readTail( stream )
      self.file_size += oversize
      self.__moveLocations( location.offset, oversize )
    
    self.file_header.save( stream )
    
    stream.seek( location.offset )
    stream.write( chunk )
  
  #//-------------------------------------------------------//
  
  def   __delitem__(self, key):
    stream = self.stream
    location = self.locations[key]
    
    tail = location.readTail( stream )
    offset = location.offset
    
    self.file_header.save( stream )
    
    stream.seek( offset )
    stream.write( tail )
    stream.truncate( offset + len(tail) )
    
    self.__moveLocations( offset, -location.chunkSize() )
    
    del self.locations[ key ]
    
  #//-------------------------------------------------------//
  
  def   __getitem__(self, key ):
    return self.locations[ key ].data()
  
  #//-------------------------------------------------------//
  
  def   __iter__(self):
    for location in self.locations:
      yield location.data()
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return len( self.locations )
  
  #//-------------------------------------------------------//
  
  def   __bool__(self):
    return bool(self.locations)
  
  #//-------------------------------------------------------//
  
  def   selfTest( self ):
    file_size = self.file_header_size
    
    for offset, reserved_data_size, data_size, version in self.locations:
      if reserved_data_size < data_size:
        raise AssertionError("reserved_data_size < data_size")
      
      file_size += self.header_size + reserved_data_size
    
    if file_size != self.file_size:
      raise AssertionError("file_size (%s) != self.file_size (%s)" % (file_size, self.file_size) )
    
    if self.stream is not None:
      real_file_size = self.stream.seek( 0, os.SEEK_END )
      if self.locations:
        last_offset, last_reserved_data_size, last_data_size, version = self.locations[-1]
        last_data_offset = last_offset + self.header_size
        
        if real_file_size < (last_data_offset + last_data_size) or \
           real_file_size > (last_data_offset + last_reserved_data_size) :
          raise AssertionError("Invalid real_file_size(%s), last_data_offset: %s, last_data_size: %s, last_reserved_data_size: %s" %
                                (real_file_size, last_data_offset, last_data_size, last_reserved_data_size) )
      
      else:
        if file_size != real_file_size:
          raise AssertionError("file_size != real_file_size")
    
    prev_offset = self.file_header_size
    prev_reserved_data_size = -self.header_size
    for offset, reserved_data_size, data_size, version in self.locations:
      if (prev_offset + prev_reserved_data_size + self.header_size) != offset:
        raise AssertionError("(prev_offset (%s) + prev_reserved_data_size(%s) + self.header_size(%s)) != offset (%s)" %
                             (prev_offset, prev_reserved_data_size, self.header_size, offset))
      prev_offset = offset
      prev_reserved_data_size = reserved_data_size
    
    #//-------------------------------------------------------//
    
    
    version, offset = self.__readFileVersion()
    index = 0
    
    while True:
      version, reserved_data_size, data_size = self.__readHeader( offset )
      if not reserved_data_size:
        break
      
      location = [offset, reserved_data_size, data_size, version ]
      
      if self.locations[index] != location:
        raise AssertionError("self.locations[%s] (%s) != location (%s)" % (index, self.locations[index], location))
      
      offset += self.header_size + reserved_data_size
      index += 1

