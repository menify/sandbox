import sys
import os.path
import pickle
import timeit

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import testcase, skip, runTests
from aql_temp_file import Tempfile
from aql_value import Value, NoContent
from aql_str_value import StringValue, StringContentIgnoreCase
from aql_file_value import FileValue, FileContentTimeStamp
from aql_value_pickler import ValuePickler, pickleable


#//===========================================================================//

@testcase
def test_value_pickler(self):
  
  with Tempfile() as tmp:
    vpick = ValuePickler()
    value = FileValue( tmp.name )
    
    vl = vpick.dumps( value )
    vl = vpick.dumps( value )
    vl = vpick.dumps( value )
    
    v = vpick.loads( vl )
    v = vpick.loads( vl )
    v = vpick.loads( vl )
    self.assertEqual( value, v )
    self.assertEqual( value.content, v.content )
    
    value = FileValue( tmp.name, FileContentTimeStamp )
    v = vpick.loads( vpick.dumps( value ) )
    self.assertEqual( value, v )
    self.assertEqual( value.content, v.content )
  
  value = StringValue( tmp.name, '123-345' )
  v = vpick.loads( vpick.dumps( value ) )
  self.assertEqual( value, v )
  self.assertEqual( value.content, v.content )
  
  value = StringValue( tmp.name, StringContentIgnoreCase('123-345') )
  v = vpick.loads( vpick.dumps( value ) )
  self.assertEqual( value, v )
  self.assertEqual( value.content, v.content )
  
  value = StringValue( tmp.name, None )
  v = vpick.loads( vpick.dumps( value ) )
  self.assertEqual( value, v )
  self.assertIsInstance( v.content, NoContent )
  
  value = Value( "1221", 12345 )
  v = vpick.loads( vpick.dumps( value ) )
  self.assertEqual( value, v )
  self.assertEqual( value.content, v.content )
  

#//===========================================================================//

@skip
@testcase
def test_value_pickler_speed( self ):
  
  with Tempfile() as tmp:
    tmp = Tempfile()
    
    vpick = ValuePickler()
    value = FileValue( tmp.name )
    
    def   test_speed( pload, pdump, value ):
      pload( pdump( value ) )
    
    t = lambda pload = vpick.loads, pdump = vpick.dumps, value = value: test_speed( pload, pdump, value )
    t = timeit.timeit( t, number = 10000 )
    print("vpick: %s" % t)
    
    t = lambda pload = pickle.loads, pdump = pickle.dumps, value = value: test_speed( pload, pdump, value )
    t = timeit.timeit( t, number = 10000 )
    print("vpick: %s" % t)
  
  vl = vpick.dumps( value )
  print("vl: %s" % len(vl))
  
  pl = pickle.dumps( value )
  print("pl: %s" % len(pl))


#//===========================================================================//

if __name__ == "__main__":
  runTests()
