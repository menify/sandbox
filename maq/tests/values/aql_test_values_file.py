import sys
import os.path
import uuid

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import testcase, skip, runTests
from aql_temp_file import Tempfile
from aql_depends_value import DependsValue
from aql_str_value import StringValue
from aql_data_file import DataFile
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

@testcase
def test_values_file(self):
  
  with Tempfile() as temp_file:
  
    temp_file_name = temp_file.name
    vf = ValuesFile( temp_file_name ); vf.selfTest()
    
    values = generateStringValues(100)
    for value in values:
      vf.add( value ); vf.selfTest()
      self.assertIs( vf.find( value ), value )
    
    file_size = float(os.stat( temp_file_name ).st_size) / 1000
    print( "File size: %s" % file_size )
    
    vf.open( temp_file_name ); vf.selfTest()
    
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
    
    vf.open( temp_file_name ); vf.selfTest()
    
    for value in all_values:
      self.assertIsNotNone( vf.find( value ) )
    
    df = DataFile( temp_file_name ); df.selfTest()
    del df[1]
    df.close(); df.selfTest()
    vf.open( temp_file_name ); vf.selfTest()
    
    self.assertEqual( len(vf), 2 )
    
    for value in (all_values[0], all_values[2]):
      self.assertIsNotNone( vf.find( value ) )
    
    for value in [all_values[1]] + depends_values + depends_values2:
      self.assertIsNone( vf.find( value ) )

#//===========================================================================//

@testcase
def test_values_file_depends2(self):
  
  with Tempfile() as temp_file:
  
    temp_file_name = temp_file.name
    
    values = generateStringValues(10)
    dep_values = generateDependsValues( 10, values )
    dep_values2 = generateDependsValues( 10, values + dep_values )
    dep_values3 = generateDependsValues( 10, values + dep_values2 )
    
    all_values = values + dep_values + dep_values2 + dep_values3
    
    vf = ValuesFile( temp_file_name )
    
    for value in values + dep_values2:
      vf.add( value ); vf.selfTest()
    
    file_size = float(os.stat( temp_file_name ).st_size) / 1000
    print( "File size: %s" % file_size )
    
    vf.open( temp_file_name ); vf.selfTest()
    
    vf.clear()
    
    for value in all_values:
      vf.add( value ); vf.selfTest()
    
    vf.open( temp_file_name ); vf.selfTest()

#//===========================================================================//

@skip
@testcase
def test_values_file_speed(self):
  
  with Tempfile() as temp_file:
  
    temp_file_name = temp_file.name
    
    values = generateStringValues(20)
    dep_values = generateDependsValues( 10, values )
    dep_values2 = generateDependsValues( 10, values + dep_values )
    dep_values3 = generateDependsValues( 10000, values + dep_values2 )
    other_values = generateStringValues( 100000 )
    
    all_values = values + dep_values + dep_values2 + dep_values3 + other_values
    
    vf = ValuesFile( temp_file_name )
    
    for value in all_values:
      vf.add( value )
    
    file_size = float(os.stat( temp_file_name ).st_size) / 1000
    print( "File size: %s" % file_size )
    
    l = lambda vf = vf, temp_file_name = temp_file_name: vf.open( temp_file_name )
    
    from timeit import Timer
    t = Timer( l )
    print("open time: %s" % (t.timeit(5) / 5,) )

#//===========================================================================//

if __name__ == "__main__":
  runTests()
