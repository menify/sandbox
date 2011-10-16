import os
import sys

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import testcase, runTests
from aql_hash import Hash

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
def test_hash(self):
  items_hash = Hash()
  
  item1 = Item('test', 'value1')
  item2 = Item('test', 'value2')
  item2_ = Item('test', 'value2')
  item3 = Item('test3', 'value2')
  
  items_hash.selfTest()
  
  items_hash[ 1 ]= item1; self.assertIn( item1, items_hash ); self.assertEqual( items_hash.find( item1 ), ( 1, item1 ) );
  items_hash.selfTest()
  
  items_hash[ 2 ]= item2; self.assertIn( item2, items_hash ); self.assertEqual( items_hash.find( item2 ), ( 2, item2 ) ); self.assertIn( item2_, items_hash )
  items_hash.selfTest()
  
  items_hash[ 3 ]= item3; self.assertIn( item3, items_hash ); self.assertEqual( items_hash.find( item3 ), ( 3, item3 ) );
  items_hash.selfTest()
  
  found_item2_key, found_item2 = items_hash.find( item2_ ); self.assertEqual( found_item2_key, 2 ); self.assertIs( found_item2, item2 )
  
  self.assertEqual( len(items_hash), 3 )
  self.assertTrue( items_hash )
  
  count = 0
  for i in items_hash:
    count += 1
  
  self.assertEqual( len(items_hash), count )
  
  new_item1 = Item('testing', 'value')
  items_hash[ 1 ] = new_item1; items_hash.selfTest()
  self.assertEqual( items_hash.find( item1 ), (None, None) )
  self.assertEqual( items_hash.find( new_item1 ), (1, new_item1) );
  
  items_hash[ 11 ] = new_item1; items_hash.selfTest()
  self.assertEqual( items_hash.find( new_item1 ), (11, new_item1) )
  with self.assertRaises( KeyError ): items_hash[1]
  
  items_hash.remove( item2 ); items_hash.selfTest()
  items_hash.remove( item2 ); items_hash.selfTest()
  with self.assertRaises( KeyError ): del items_hash[2]
  items_hash.selfTest()
  
  del items_hash[3]; items_hash.selfTest()
  with self.assertRaises( KeyError ): del items_hash[3]
  items_hash.selfTest()
  
  self.assertEqual( len(items_hash), 1 )
  
  items_hash.clear(); items_hash.selfTest()
  
  self.assertEqual( items_hash.find( item1 ), (None, None))
  self.assertNotIn( item1, items_hash )
  self.assertEqual( len(items_hash), 0 )
  self.assertFalse( items_hash )
  
#//===========================================================================//

if __name__ == "__main__":
  runTests()
