import sys
import os.path
import uuid

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import testcase, runTests
from aql_temp_file import Tempfile
from aql_file_value import FileValue, FileName, FileContentChecksum, FileContentTimeStamp
from aql_str_value import StringValue
from aql_values_file import ValuesFile

#//===========================================================================//

def   generateStringValues( num_of_values ):
  values = []
  for i in range(0, num_of_values):
    value = StringValue( "name_" + uuid.uuid4().hex, "content_" + uuid.uuid4().hex )
    values.append( value )
  
  return values

#//===========================================================================//

@testcase
def test_values_file(self):
  
  with Tempfile() as temp_file:
  
    temp_file_name = temp_file.name
    vf = ValuesFile( temp_file_name ); vf.selfTest()
    
    values = generateStringValues(1000)
    for value in values:
      vf.add( value ); vf.selfTest()
      self.assertIs( vf.find( value ), value )
    
    file_size = float(os.stat( temp_file_name ).st_size) / 1000
    print( "File size: %s" % file_size )
    
    vf.load( temp_file_name ); vf.selfTest()
    
    for value in values:
      self.assertIsNotNone( vf.find( value ) )
    
    for value in values:
      value.content = "content_" + uuid.uuid4().hex * 2
      vf.update( value ); vf.selfTest()
      self.assertIs( vf.find( value ), value )


#//===========================================================================//

if __name__ == "__main__":
  runTests()
