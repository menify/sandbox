import sys
import os.path
import timeit
try:
  import cPickle as pickle
except ImportError:
  import pickle

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import skip, AqlTestCase, runLocalTests

from aql.utils import Tempfile
from aql.values import FileChecksumValue, FileTimestampValue, SimpleValue, ValuePickler, pickleable

#//===========================================================================//

class TestValuePickler( AqlTestCase ):
  def test_value_pickler(self):
    
    with Tempfile() as tmp:
      tmp_name = str(tmp)
      vpick = ValuePickler()
      value = FileChecksumValue( tmp )
      
      vl = vpick.dumps( value )
      vl = vpick.dumps( value )
      vl = vpick.dumps( value )
      
      v = vpick.loads( vl )
      v = vpick.loads( vl )
      v = vpick.loads( vl )
      self.assertEqual( value, v )
      
      value = FileTimestampValue( tmp )
      v = vpick.loads( vpick.dumps( value ) )
      self.assertEqual( value, v )
    
    value = SimpleValue( '123-345', name = tmp_name )
    v = vpick.loads( vpick.dumps( value ) )
    self.assertEqual( value, v )
    
    value = SimpleValue( '123-345', name = tmp_name )
    v = vpick.loads( vpick.dumps( value ) )
    self.assertEqual( value, v )
    
    value = SimpleValue( name = tmp_name )
    v = vpick.loads( vpick.dumps( value ) )
    self.assertEqual( value.name, v.name )
    self.assertTrue( v.isNull() )
    
    #value = Value( "1221", 12345 )
    #v = vpick.loads( vpick.dumps( value ) )
    #self.assertEqual( value, v )

  #//===========================================================================//

  @skip
  def test_value_pickler_speed( self ):
    
    with Tempfile() as tmp:
      
      vpick = ValuePickler()
      value = FileChecksumValue( tmp )
      
      t = lambda pload = vpick.loads, pdump = vpick.dumps, value = value: pload( pdump( value ) )
      t = timeit.timeit( t, number = 10000 )
      print("value picker: %s" % t)
      
      t = lambda pload = pickle.loads, pdump = pickle.dumps, value = value: pload( pdump( value, protocol = pickle.HIGHEST_PROTOCOL ) )
      t = timeit.timeit( t, number = 10000 )
      print("pickle: %s" % t)
    
    vl = vpick.dumps( value )
    print("vl: %s" % len(vl))
    
    pl = pickle.dumps( value, protocol = pickle.HIGHEST_PROTOCOL )
    print("pl: %s" % len(pl))

#//===========================================================================//

if __name__ == "__main__":
  runLocalTests()
