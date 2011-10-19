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
  header_size = header_struct.size
  
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
    
    oversize = 0
    
    capacity = self.capacity
    if capacity < size:
      self.capacity = size + size // 2
      oversize = self.capacity - capacity
    
    self.size = size
    
    header = header_struct.pack( key, self.version, self.capacity, size )
    
    chunk = bytearray(header)
    chunk += data
    
    return chunk, oversize
  
  #//-------------------------------------------------------//
  
  def   data( self, stream, header_size = header_size ):
    stream.seek( self.offset + header_size )
    return stream.read( self.size )
  
  #//-------------------------------------------------------//
  
  def   chunkSize( self, header_size = header_size ):
    return header_size + self.capacity
  
  #//-------------------------------------------------------//
  
  def   __str__(self):
    s = []
    for v in self.__slots__:
      s.append( v + ": " + str(getattr( self, v )) ) 
    
    return ", ".join( s )

#//===========================================================================//

class _DFHeader( object ):
  
  __slots__ = \
  (
    'version',
    'uid',
  )
  
  header_struct = struct.Struct(">LQ") # big-endian, 4 bytes (file version), 8 bytes (next unique ID)
  header_size = header_struct.size
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
      return True, header_size
    
    version = self.version
    self.version, self.uid = header_struct.unpack( header )
    
    return (version != self.version)
  
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
    
    self.save( stream )
    
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
  
  def   __init__( self, filename, DataFileHeader = _DFHeader ):
    
    self.locations = {}
    self.file_header = DataFileHeader()
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
    
    self.file_header.load( stream )
    
    offset = self.file_header.header_size
    stream = self.stream
    locations = self.locations
    
    while True:
      key, location, size = loadLocation( stream, offset )
      if key == -1:
        break
      
      locations[key] = location
      offset += size
    
    self.file_size = offset
  
  #//-------------------------------------------------------//
  
  def   update(self, loadLocation = _DFLocation.load ):
    if self.file_header.load( self.stream ):
      return [], [], []
    
    offset = self.file_header.header_size
    
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
  
  def append( self, data, Location = _DFLocation):
    
    stream  = self.stream
    key     = self.file_header.nextKey( stream )
    offset  = self.file_size
    
    location = Location( offset )
    
    chunk, oversize = location.pack( key, data )
    
    stream.seek( offset )
    stream.write( chunk )
    
    self.file_size += location.chunkSize()
    self.locations[key] = location
    
    return key
  
  #//-------------------------------------------------------//
  
  def   __setitem__(self, key, data ):
    
    location = self.locations[ key ]
    tail_offset = location.offset + location.chunkSize()
    
    chunk, oversize = location.pack( key, data )
    
    stream = self.stream
    
    if oversize > 0:
      chunk += bytearray( location.capacity - location.size )
      
      stream.seek( tail_offset ); chunk += stream.read()
      
      self.file_size += oversize
      self.__moveLocations( location.offset, oversize )
      
    self.file_header.save( stream )
    
    stream.seek( location.offset )
    stream.write( chunk )
  
  #//-------------------------------------------------------//
  
  def   __delitem__(self, key):
    stream = self.stream
    location = self.locations[key]
    
    chunk_size = location.chunkSize()
    offset = location.offset
    
    stream.seek( offset + chunk_size ); tail = stream.read()
    
    self.file_header.save( stream )
    
    stream.seek( offset )
    stream.write( tail )
    stream.truncate( offset + len(tail) )
    
    self.__moveLocations( offset, -chunk_size )
    self.file_size -= chunk_size
    
    del self.locations[ key ]
    
  #//-------------------------------------------------------//
  
  def   __getitem__(self, key ):
    return self.locations[ key ].data( self.stream )
  
  #//-------------------------------------------------------//
  
  def   __iter__(self):
    for key, location in self.locations.items():
      yield key, location.data( self.stream )
  
  #//-------------------------------------------------------//
  
  def   __len__(self):
    return len( self.locations )
  
  #//-------------------------------------------------------//
  
  def   __bool__(self):
    return bool(self.locations)
  
  #//-------------------------------------------------------//
  
  def   selfTest( self ):
    
    if self.stream is not None:
      file_size = self.file_header.header_size
    else:
      file_size = 0
    
    for location in self.locations.values():
      if location.capacity < location.size:
        raise AssertionError("location.capacity(%s) < location.size (%s)" % (location.capacity, location.size))
      
      file_size += location.chunkSize()
    
    if file_size != self.file_size:
      raise AssertionError("file_size (%s) != self.file_size (%s)" % (file_size, self.file_size) )
    
    ordered_location = sorted( self.locations.values(), key = lambda l: l.offset )
    
    if self.stream is not None:
      real_file_size = self.stream.seek( 0, os.SEEK_END )
      if ordered_location:
        
        last_location = ordered_location[-1]
        last_data_offset = last_location.offset + last_location.header_size
        
        if real_file_size < (last_data_offset + last_location.size) or \
           real_file_size > (last_data_offset + last_location.capacity) :
          raise AssertionError("Invalid real_file_size(%s), last_location: %s" % (real_file_size, last_location) )
      
      else:
        if file_size != real_file_size:
          raise AssertionError("file_size != real_file_size")
    
    prev_location = None
    for location in self.locations.values():
      if prev_location is not None:
        if (prev_location.offset + prev_location.capacity + prev_location.header_size) != location.offset:
          raise AssertionError("Messed locations: %s %s" % (prev_location, location))
      
      prev_location = location
    
    #//-------------------------------------------------------//
    
    if self.stream is not None:
      self.file_header.load( self.stream )
      offset = self.file_header.header_size
      
      while True:
        key, location, size = _DFLocation.load( self.stream, offset )
        if key == -1:
          break
        
        l = self.locations[key]
        
        if (l.version != location.version) or \
           (l.size != location.size) or \
           (l.capacity != location.capacity) :
          raise AssertionError("self.locations[%s] (%s) != location (%s)" % (key, l, location))
        
        offset += size
