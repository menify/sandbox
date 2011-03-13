
import os
import hashlib

import Value

#//===========================================================================//

class   FileContentChecksum (object):
    
    __slots__ = ( 'size', 'checksum' )
    
    def   __init__( self, path ):
        
        size = os.stat( path ).st_size
        
        checksum = hashlib.md5()
        
        for chunk in open( path, mode = 'rb' ):
            checksum.update( chunk )
        
        self.checksum = checksum
        self.size = size
    
    #//-------------------------------------------------------//
    
    def   __eq__( self, other ):          return (self.size == other.size) and (self.checksum == other.checksum)
    def   __ne__( self, other ):          return (self.size != other.size) or (self.checksum != other.checksum)
    def   __getstate__( self ):           return { 'size': self.size, 'checksum': self.checksum }
    def   __setstate__( self, state ):    self.size = state['size']; self.checksum = state['checksum']

#//===========================================================================//

class   FileContentTimeStamp (object):
    
    __slots__ = ( 'size', 'modify_time' )
    
    def   __init__( self, path ):
        stat = os.stat( path )
        
        self.size = stat.st_size
        self.modify_time = stat.st_mtime
    
    #//-------------------------------------------------------//
    
    def   __eq__( self, other ):          return (self.size == other.size) and (self.modify_time == other.modify_time)
    def   __ne__( self, other ):          return (self.size != other.size) or (self.modify_time != other.modify_time)
    def   __getstate__( self ):           return { 'size': self.size, 'modify_time': self.modify_time }
    def   __setstate__( self, state ):    self.size = state['size']; self.modify_time = state['modify_time']

#//===========================================================================//

class   File (Value):
    
    __slots__ = ( 'path', 'content' )
    
    def   __init__( self, path, file_content = FileContentChecksum ) :
        self.path = os.path.abspath( path )
        self.content = file_content( path )
    
    #//-------------------------------------------------------//
    
    def   __getstate__( self ):
        return { 'path': self.path, 'content' : self.content }
    
    #//-------------------------------------------------------//
    
    def   __setstate__( self, state ):
        self.path = state['path']
        self.content = state['content']
    
    #//-------------------------------------------------------//
    
    def   __lt__( self, other):       return self.path < other.path
    def   __le__( self, other):       return self.path <= other.path
    def   __eq__( self, other):       return self.path == other.path
    def   __ne__( self, other):       return self.path != other.path
    def   __gt__( self, other):       return self.path > other.path
    def   __ge__( self, other):       return self.path >= other.path
