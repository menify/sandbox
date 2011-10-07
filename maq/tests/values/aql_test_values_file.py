import sys
import os.path
import uuid

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import testcase, skip, runTests
from aql_temp_file import Tempfile
from aql_depends_value import DependsValue
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

def   generateDependsValues( num_of_values, values ):
  depends_values = []
  for i in range(0, num_of_values):
    
    depends_value = DependsValue( "depends_value_name_" + uuid.uuid4().hex, values )
    depends_values.append( depends_value )
  
  return depends_values

#//===========================================================================//
@skip
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

@testcase
def test_values_file_depends(self):
  
  with Tempfile() as temp_file:
  
    temp_file_name = temp_file.name
    vf = ValuesFile( temp_file_name ); vf.selfTest()
    
    values = generateStringValues(3)
    depends_values = generateDependsValues( 3, values )
    depends_values2 = generateDependsValues( 3, values + depends_values )
    
    all_values = values + depends_values + depends_values2
    
    for value in all_values:
      vf.add( value ); vf.selfTest()
      self.assertIs( vf.find( value ), value )
    
    file_size = float(os.stat( temp_file_name ).st_size) / 1000
    print( "File size: %s" % file_size )
    
    vf.load( temp_file_name ); vf.selfTest()
    
    for value in all_values:
      self.assertIsNotNone( vf.find( value ) )


#//===========================================================================//

if __name__ == "__main__":
  runTests()
