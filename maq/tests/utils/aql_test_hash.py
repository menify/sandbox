
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
  
  hash.add( item1 )
  hash.add( item2 )
  hash.add( item2_ )
  hash.add( item3 )
  
  self.assertEqual( len(hash), 3 )
  self.assertTrue( hash )
  
  self.assertIsNotNone( hash.find( item1 ) )
  self.assertIsNotNone( hash.find( item2 ) )
  self.assertIsNotNone( hash.find( item3 ) )
  
  self.assertIn( item1, hash )
  self.assertIn( item2, hash )
  self.assertIn( item3, hash )
  
  count = 0
  for i in hash:
    count += 1
  
  self.assertEqual( len(hash), count )
  
  hash.remove( item1 )
  self.assertIsNone( hash.find( item1 ) )
  self.assertNotIn( item1, hash )
  
  hash.remove( item2 )
  self.assertIsNone( hash.find( item2 ) )
  self.assertNotIn( item2, hash )
  
  hash.remove( item3 )
  self.assertIsNone( hash.find( item3 ) )
  self.assertNotIn( item3, hash )
  
  self.assertEqual( len(hash), 0 )
  self.assertFalse( hash )
  
  hash.add( item1 )
  
  self.assertEqual( len(hash), 1 )
  self.assertTrue( hash )
  
  hash.clear()
  
  self.assertIsNone( hash.find( item1 ) )
  self.assertNotIn( item1, hash )
  self.assertEqual( len(hash), 0 )
  self.assertFalse( hash )
  
#//===========================================================================//
