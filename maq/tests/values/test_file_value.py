import io
import sys
import time
import pickle
import os.path

from test_suite import testcase
from aql_temp_file import Tempfile
from aql_file_value import FileValue, FileName, FileContentChecksum, FileContentTimeStamp
from aql_logging import logDebug, logError

@testcase
def test_file_value(self):
  with Tempfile() as temp_file:
    test_string = '1234567890'
    
    temp_file.write( test_string.encode() )
    temp_file.flush()

    temp_file_value1 = FileValue( temp_file.name )
    temp_file_value2 = FileValue( temp_file.name )
    
    self.assertEqual( temp_file_value1, temp_file_value2 )
    self.assertEqual( temp_file_value1.content, temp_file_value2.content )
    
    reversed_test_string = str(reversed(test_string))
    temp_file.seek( 0 )
    temp_file.write( reversed_test_string.encode() )
    temp_file.flush()
    
    temp_file_value2 = FileValue( temp_file_value1 )
    self.assertEqual( temp_file_value1, temp_file_value2 )
    self.assertNotEqual( temp_file_value1.content, temp_file_value2.content )

  #//=======================================================//

@testcase
def test_file_value_save_load(self):
  
  temp_file_name = None
  
  with Tempfile() as temp_file:
    test_string = '1234567890'
    
    temp_file.write( test_string.encode() )
    temp_file.flush()
    
    temp_file_name = temp_file.name
    
    temp_file_value = FileValue( temp_file_name )
    
  with io.BytesIO() as saved_status:
    saver = pickle.Pickler( saved_status, protocol = pickle.HIGHEST_PROTOCOL )
    saver.dump( ( temp_file_value, ) )
    
    saved_status.seek(0)
    
    loader = pickle.Unpickler( saved_status )
    loaded_values = loader.load()
    loaded_file_value = loaded_values[0]
    
    self.assertEqual( temp_file_value, loaded_file_value )
    self.assertEqual( temp_file_value.content, loaded_file_value.content )
  
  temp_file_value = FileValue( temp_file_name )
  self.assertEqual( temp_file_value, loaded_file_value )
  self.assertNotEqual( temp_file_value.content, loaded_file_value.content )
  self.assertFalse( temp_file_value.exists() )

#//=======================================================//

@testcase
def test_file_value_time(self):
  with Tempfile() as temp_file:
    test_string = '1234567890'
    
    temp_file.write( test_string.encode() )
    temp_file.flush()

    temp_file_value1 = FileValue( temp_file.name, FileContentTimeStamp )
    temp_file_value2 = FileValue( temp_file.name, FileContentTimeStamp )
    
    self.assertEqual( temp_file_value1, temp_file_value2 )
    self.assertEqual( temp_file_value1.content, temp_file_value2.content )
    
    time.sleep(1)
    temp_file.seek( 0 )
    temp_file.write( test_string.encode() )
    temp_file.flush()
    
    temp_file_value2 = FileValue( temp_file_value1, FileContentTimeStamp )
    self.assertEqual( temp_file_value1, temp_file_value2 )
    self.assertNotEqual( temp_file_value1.content, temp_file_value2.content )

#//=======================================================//

@testcase
def test_file_value_time_save_load(self):
  
  temp_file_name = None
  
  with Tempfile() as temp_file:
    test_string = '1234567890'
    
    temp_file.write( test_string.encode() )
    temp_file.flush()
    
    temp_file_name = temp_file.name
    
    temp_file_value = FileValue( temp_file_name, FileContentTimeStamp )
    
  with io.BytesIO() as saved_status:
    saver = pickle.Pickler( saved_status, protocol = pickle.HIGHEST_PROTOCOL )
    saver.dump( ( temp_file_value, ) )
    
    saved_status.seek(0)
    
    loader = pickle.Unpickler( saved_status )
    loaded_values = loader.load()
    loaded_file_value = loaded_values[0]
    
    self.assertEqual( temp_file_value, loaded_file_value )
    self.assertEqual( temp_file_value.content, loaded_file_value.content )
  
  temp_file_value = FileValue( temp_file_name, FileContentTimeStamp )
  self.assertEqual( temp_file_value, loaded_file_value )
  self.assertNotEqual( temp_file_value.content, loaded_file_value.content )
  self.assertFalse( temp_file_value.exists() )
