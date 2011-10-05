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

def   generateStringValues():
  values = []
  for i in range(0, 100):
    value = StringValue( "name_" + uuid.uuid4(), "content_" + uuid.uuid4() )
    values.append( value )
  
  return values

#//===========================================================================//

@testcase
def test_values_file(self):
  
  with Tempfile() as temp_file:
    
    temp_file.remove()
    
    vf = ValuesFile( temp_file.name )


if __name__ == "__main__":
  runTests()
