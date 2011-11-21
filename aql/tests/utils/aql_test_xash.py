import os
import sys

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import testcase, runTests
from aql_xash import Xash

#//===========================================================================//

class Item (object):
  
  __slots__ = ('name', 'value')
  
  def  __init__(self, name, value ):
    self.name = name
    self.value = value
  
  def __hash__(self):
    return hash(self.name)
  
  def __eq__(self, other):
    return (self.name == other.name) and (self.value == other.value)
  
  def __ne__(self, other):
    return not self.__eq__(self, other)
  
  def __str__(self):
    return str(self.name) + ":" + str(self.value)

#//===========================================================================//

@testcase
def test_xash(self):
  items_xash = Xash()
  
  item1 = Item('test', 'value1')
  item2 = Item('test', 'value2')
  item2_ = Item('test', 'value2')
  item3 = Item('test3', 'value2')
  
  xash.selfTest()
  
  xash[ 1 ]= item1; self.assertIn( item1, xash ); self.assertEqual( xash.find( item1 ), ( 1, item1 ) );
  xash[ 1 ]= item1; self.assertIn( item1, xash ); self.assertEqual( xash.find( item1 ), ( 1, item1 ) );
  xash.selfTest()
  
  xash[ 2 ]= item2; self.assertIn( item2, xash ); self.assertEqual( xash.find( item2 ), ( 2, item2 ) ); self.assertIn( item2_, xash )
  xash.selfTest()
  
  xash[ 3 ]= item3; self.assertIn( item3, xash ); self.assertEqual( xash.find( item3 ), ( 3, item3 ) );
  xash.selfTest()
  
  found_item2_key, found_item2 = xash.find( item2_ ); self.assertEqual( found_item2_key, 2 ); self.assertIs( found_item2, item2 )
  
  self.assertEqual( len(xash), 3 )
  self.assertTrue( xash )
  
  count = 0
  for i in xash:
    count += 1
  
  self.assertEqual( len(xash), count )
  
  new_item1 = Item('testing', 'value')
  xash[ 1 ] = new_item1; xash.selfTest()
  self.assertEqual( xash.find( item1 ), (None, None) )
  self.assertEqual( xash.find( new_item1 ), (1, new_item1) );
  
  xash[ 11 ] = new_item1; xash.selfTest()
  self.assertEqual( xash.find( new_item1 ), (11, new_item1) )
  with self.assertRaises( KeyError ): xash[1]
  
  xash.remove( item2 ); xash.selfTest()
  xash.remove( item2 ); xash.selfTest()
  with self.assertRaises( KeyError ): del xash[2]
  xash.selfTest()
  
  del xash[3]; xash.selfTest()
  with self.assertRaises( KeyError ): del xash[3]
  xash.selfTest()
  
  self.assertEqual( len(xash), 1 )
  
  xash.clear(); xash.selfTest()
  
  self.assertEqual( xash.find( item1 ), (None, None))
  self.assertNotIn( item1, xash )
  self.assertEqual( len(xash), 0 )
  self.assertFalse( xash )
  
#//===========================================================================//

if __name__ == "__main__":
  runTests()