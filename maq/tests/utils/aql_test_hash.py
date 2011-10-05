
from aql_hash import Hash
from aql_tests import testcase

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
  hash = Hash()
  
  item1 = Item('test', 'value1')
  item2 = Item('test', 'value2')
  item2_ = Item('test', 'value2')
  item3 = Item('test3', 'value2')
  
  hash.selfTest()
  
  item_key1, item1 = hash.add( item1 ); hash.selfTest()
  item_key2, item2 = hash.add( item2 ); hash.selfTest()
  item_key2_, item2_ = hash.add( item2_ ); hash.selfTest()
  item_key3, item3 = hash.add( item3 ); hash.selfTest()
  
  self.assertIs( item2, item2_ )
  self.assertEqual( item_key2, item_key2_ )
  
  self.assertEqual( len(hash), 3 )
  self.assertTrue( hash )
  
  self.assertIsNotNone( hash.find( item1 )[0] )
  self.assertIsNotNone( hash.find( item2 )[0] )
  self.assertIsNotNone( hash.find( item3 )[0] )
  
  self.assertIn( item1, hash )
  self.assertIn( item2, hash )
  self.assertIn( item3, hash )
  
  count = 0
  for i in hash:
    count += 1
  
  self.assertEqual( len(hash), count )
  
  new_item1 = Item('testing', 'value')
  hash[ item_key1 ] = new_item1; hash.selfTest()
  self.assertEqual( hash.find( item1 ), (None, None) )
  
  item1 = new_item1
  
  hash[ item_key2 ] = item1; hash.selfTest()
  self.assertEqual( hash.find( item2 ), (None, None) )
  
  item1 = new_item1
  
  hash.remove( item1 ); hash.selfTest()
  self.assertEqual( hash.find( item1 ), (None, None) )
  self.assertNotIn( item1, hash )
  
  item_key1, item_old_key1 = hash.update( item1 ); hash.selfTest()
  self.assertIsNone( item_old_key1 )
  new_item_key1, item_old_key1 = hash.update( item1 ); hash.selfTest()
  self.assertEqual( item_key1, item_old_key1 )
  self.assertNotEqual( item_key1, new_item_key1 )
  self.assertIs( hash[new_item_key1], item1 )
  
  del hash[ new_item_key1 ]; hash.selfTest()
  
  hash.remove( item2 ); hash.selfTest()
  self.assertEqual( hash.find( item2 ), (None, None) )
  self.assertNotIn( item2, hash )
  
  hash.remove( item3 ); hash.selfTest()
  self.assertEqual( hash.find( item3 ), (None, None))
  self.assertNotIn( item3, hash )
  
  self.assertEqual( len(hash), 0 )
  self.assertFalse( hash )
  
  hash.add( item1 ); hash.selfTest()
  
  self.assertEqual( len(hash), 1 )
  self.assertTrue( hash )
  
  hash.clear(); hash.selfTest()
  
  self.assertEqual( hash.find( item1 ), (None, None))
  self.assertNotIn( item1, hash )
  self.assertEqual( len(hash), 0 )
  self.assertFalse( hash )
  
#//===========================================================================//
