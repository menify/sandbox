import io
import sys
import os.path
import tempfile
import pickle

sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', '..', 'utils') )
sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', '..', 'values') )

from aql_logging import logDebug, logError
from aql_file_value import FileValue, FileName, FileContentChecksum, FileContentTimeStamp

#//===========================================================================//

def   test():
  with io.BytesIO() as file:
    with tempfile.NamedTemporaryFile( delete = False ) as temp_file:
      
      temp_file.write( '1234567890\n1234567890'.encode() )
      temp_file.flush()
      
      temp_file_name = FileName( temp_file.name )
      
      temp_file_value = FileValue( temp_file_name )
      logDebug( "temp_file_value: %s, %s", temp_file_value, temp_file_value.content )
      
      temp_file.close()
      os.remove( temp_file_name )
      
      saver = pickle.Pickler( file, protocol = pickle.HIGHEST_PROTOCOL )
      saver.dump( ( temp_file_value, ) )
      
      file.seek(0)
      
      loader = pickle.Unpickler( file )
      loaded_values = loader.load()
      value = loaded_values[0]
      logDebug( "value: %s, %s", value, value.content )
      
      new_value = FileValue( value )
      
      logDebug( "new_value: %s, %s", new_value, new_value.content )
      
      logDebug( "new_value == value: %s", new_value == value )
      logDebug( "new_value.content == value.content: %s", new_value.content == value.content )
      logDebug( "value.content == new_value.content: %s", value.content == new_value.content )
      

if __name__ == "__main__":
  
  logError( "test logging" )
  test()
