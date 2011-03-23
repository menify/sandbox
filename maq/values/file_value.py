
import os
import hashlib
import datetime

class FileContentNotExists( object ):
    def   __eq__( self, other ):    return False
    def   __ne__( self, other ):    return True
    def   __str__( self ):          return "<Not exists>"


#//===========================================================================//

class   FileContentChecksum (object):
    
    __slots__ = ( 'size', 'checksum' )
    
    def   __new__( cls, path = None ):
        
        if path is None:
            return super(FileContentChecksum, cls).__new__(cls)
        
        try:
            size = os.stat( path ).st_size
            
            checksum = hashlib.md5()
            
            with open( path, mode = 'rb' ) as f:
                for chunk in f:
                    checksum.update( chunk )
            
            self = super(FileContentChecksum, cls).__new__(cls)
            
            self.checksum = checksum.hexdigest()
            self.size = size
            
            return self
        
        except OSError:
            return FileContentNotExists()
    
    #//-------------------------------------------------------//
    
    def   __eq__( self, other ):          return (self.size == other.size) and (self.checksum == other.checksum)
    def   __ne__( self, other ):          return (self.size != other.size) or (self.checksum != other.checksum)
    def   __getstate__( self ):           return { 'size': self.size, 'checksum': self.checksum }
    def   __setstate__( self, state ):    self.size = state['size']; self.checksum = state['checksum']
    
    def   __str__( self ):                return repr(self.checksum)

#//===========================================================================//

class   FileContentTimeStamp (object):
    
    __slots__ = ( 'size', 'modify_time' )
    
    def   __new__( cls, path = None ):
        
        if path is None:
            return super(FileContentTimeStamp, cls).__new__(cls)
        
        try:
            stat = os.stat( path )
            
            self = super(FileContentTimeStamp, cls).__new__(cls)
            
            self.size = stat.st_size
            self.modify_time = stat.st_mtime
            
            return self
        
        except OSError:
            return FileContentNotExists()

    #//-------------------------------------------------------//
    
    def   __eq__( self, other ):          return (self.size == other.size) and (self.modify_time == other.modify_time)
    def   __ne__( self, other ):          return (self.size != other.size) or (self.modify_time != other.modify_time)
    def   __getstate__( self ):           return { 'size': self.size, 'modify_time': self.modify_time }
    def   __setstate__( self, state ):    self.size = state['size']; self.modify_time = state['modify_time']
    
    def   __str__( self ):                return str( datetime.datetime.fromtimestamp( self.modify_time ) )
    

#//===========================================================================//

class   FileName (str):
    def     __new__(cls, path = None ):
        if isinstance(path, FileName):
            return path
        
        full_path = os.path.normcase( os.path.normpath( os.path.abspath( str(path) ) ) )
        
        return super(FileName, cls).__new__(cls, full_path )
