
import os
import tempfile

class Tempfile (object):
    
    __slots__ = ('__handle','name')
    
    def   __init__(self):
        self.__handle = tempfile.NamedTemporaryFile( delete = False )
        self.name = self.__handle.name
    
    def   __enter__(self):
        print( "__enter__" )
        return self
    
    def   __exit__(self, exc_type, exc_value, traceback):
        self.close()
        os.remove( self.name )
    
    def write( self, buffer ):
        self.__handle.write( buffer )
    
    def read( self, buffer ):
        self.__handle.read( buffer )
    
    def seek( self, offset, whence = os.SEEK_SET ):
        self.__handle.read( buffer )
    
    def flush( self ):
        self.__handle.flush()

if __name__ == "__main__":
  
  with Tempfile() as t:
      t.write('1234567890\n1234567890'.encode())
      print ( t.name )
