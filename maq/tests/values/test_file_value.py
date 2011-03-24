import io
import sys
import os.path
import tempfile
import pickle
import logging

sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', '..', 'values') )

from value import Value
from file_value import FileValue, FileName, FileContentChecksum, FileContentTimeStamp

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
      
      temp_file_value = FileValue( temp_file_name )
      logger.debug( "temp_file_value: %s, %s", temp_file_value, temp_file_value.content )
      
      temp_file.close()
      os.remove( temp_file_name )
      
      saver = pickle.Pickler( file, protocol = pickle.HIGHEST_PROTOCOL )
      saver.dump( ( temp_file_value, ) )
      
      file.seek(0)
      
      loader = pickle.Unpickler( file )
      loaded_values = loader.load()
      value = loaded_values[0]
      logger.debug( "value: %s, %s", value, value.content )
      
      new_value = FileValue( value )
      
      logger.debug( "new_value: %s, %s", new_value, new_value.content )
      
      logger.debug( "new_value == value: %s", new_value == value )
      logger.debug( "new_value.content == value.content: %s", new_value.content == value.content )
      logger.debug( "value.content == new_value.content: %s", value.content == new_value.content )
      

if __name__ == "__main__":
  
  logger = init_logging()
  
  logger.error( "test logging" )
  test( logger )
