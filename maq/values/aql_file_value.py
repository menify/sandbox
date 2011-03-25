
import os
import hashlib
import datetime

from aql_value import Value

#//===========================================================================//

class   Unpickling(object):
    pass

#//===========================================================================//

class FileContentNotExists( object ):
    def   __eq__( self, other ):    return False
    def   __ne__( self, other ):    return True
    def   __str__( self ):          return "<Not exists>"


#//===========================================================================//

class   FileContentChecksum (object):
    
    __slots__ = ( 'size', 'checksum' )
    
    def   __new__( cls, path = None ):
        
        if isinstance( path, Unpickling):
            return super(FileContentChecksum, cls).__new__(cls)
        
        if path is None:
            return FileContentNotExists()
        
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
    
    def   __eq__( self, other ):        return type(self) == type(other) and (self.size == other.size) and (self.checksum == other.checksum)
    def   __ne__( self, other ):        return not self.__eq__( other )
    
    def     __getnewargs__(self):       return ( Unpickling(), )

    def   __getstate__( self ):         return { 'size': self.size, 'checksum': self.checksum }
    def   __setstate__( self, state ):  self.size = state['size']; self.checksum = state['checksum']
    
    def   __str__( self ):              return self.checksum

#//===========================================================================//

class   FileContentTimeStamp (object):
    
    __slots__ = ( 'size', 'modify_time' )
    
    def   __new__( cls, path = None ):
        
        if isinstance( path, Unpickling):
            return super(FileContentTimeStamp, cls).__new__(cls)
        
        if path is None:
            return FileContentNotExists()
        
        try:
            stat = os.stat( path )
            
            self = super(FileContentTimeStamp, cls).__new__(cls)
            
            self.size = stat.st_size
            self.modify_time = stat.st_mtime
            
            return self
        
        except OSError:
            return FileContentNotExists()

    #//-------------------------------------------------------//
    
    def   __eq__( self, other ):        return type(self) == type(other) and (self.size == other.size) and (self.modify_time == other.modify_time)
    def   __ne__( self, other ):        return not self.__eq__( other )
    
    def     __getnewargs__(self):       return ( Unpickling(), )
    def   __getstate__( self ):         return { 'size': self.size, 'modify_time': self.modify_time }
    def   __setstate__( self, state ):  self.size = state['size']; self.modify_time = state['modify_time']
    
    def   __str__( self ):              return str( datetime.datetime.fromtimestamp( self.modify_time ) )
    

#//===========================================================================//

class   FileName (str):
    def     __new__(cls, path = None, str_new_args = None ):
        if isinstance( path, FileName ):
            return path
        
        if isinstance( path, Unpickling ):
            return super(FileName, cls).__new__(cls, *str_new_args )
        
        if path is None:
            return super(FileName, cls).__new__(cls)
        
        full_path = os.path.normcase( os.path.normpath( os.path.abspath( str(path) ) ) )
        
        return super(FileName, cls).__new__(cls, full_path )
    
    #//-------------------------------------------------------//
    
    def     __getnewargs__(self):
        return ( Unpickling(), super(FileName, self).__getnewargs__() )

#//===========================================================================//

class   FileValue (Value):
    
    def   __init__( self, name, content = FileContentChecksum ):
        super( FileValue, self ).__init__( name, content )


#//===========================================================================//
