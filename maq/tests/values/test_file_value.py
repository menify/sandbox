import io
import sys
import os.path
import tempfile
import pickle
import logging

sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', '..', 'values') )

from value import Value
from file_value import FileName, FileContentChecksum, FileContentTimeStamp

#//===========================================================================//
def   init_logging():
  logger = logging.getLogger( "AQL" )
  logger.setLevel(logging.DEBUG)
  
  handler = logging.StreamHandler()
  handler.setLevel( logging.DEBUG )

  logger.addHandler( handler )
  
  return logger

#//===========================================================================//

def   test( logger ):
  with io.BytesIO() as file:
    with tempfile.NamedTemporaryFile( delete = False ) as temp_file:
      
      temp_file.write( '1234567890\n1234567890'.encode() )
      temp_file.flush()
      
      temp_file_name = FileName( temp_file.name )
      temp_file_content = FileContentChecksum( temp_file_name )
      temp_file_time_content = FileContentTimeStamp( temp_file_name )
      
      temp_file_value = Value( temp_file_name, temp_file_content )
      logger.debug( "temp_file_value: %s", temp_file_value )
      
      temp_file.close()
      os.remove( temp_file_name )
      
      saver = pickle.Pickler( file, protocol = pickle.HIGHEST_PROTOCOL )
      saver.dump( temp_file_value )
      saver.dump( temp_file_value )
      
      file.seek(0)
      
      loader = pickle.Unpickler( file )
      loaded_value = loader.load()
      logger.debug( "loaded_value: %s", loaded_value )
      
      loaded_value = loader.load()
      logger.debug( "loaded_value: %s", loaded_value )
      

if __name__ == "__main__":
  
  logger = init_logging()
  
  logger.error( "test logging" )
  test( logger )
