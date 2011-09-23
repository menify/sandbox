
import random

from aql_tests import testcase, skip
from aql_temp_file import Tempfile
from aql_data_file import DataFile

#//===========================================================================//

def   generateData( min_size, max_size ):
  b = []
  size = random.randint( min_size, max_size )
  for i in range( 0, size ):
    b.append( random.randint(0, 255) )
  
  return bytearray(b)

#//===========================================================================//

def   generateDataList( min_list_size, max_list_size, min_data_size, max_data_size ):
  bl = []
  size = random.randint( min_list_size, max_list_size )
  for i in range( 0, size ):
    bl.append( generateData( min_data_size, max_data_size ) )
  
  return bl

#//===========================================================================//

def   printFileContent( filename ):
  with open( filename, 'rb' ) as f:
    b = f.read()
    print( "%s: %s" % ( filename, b ))

#//===========================================================================//

@testcase
def test_data_file(self):
  with Tempfile() as tmp:
    tmp.remove()
    
    data_list = generateDataList( 50, 50, 7, 57 )
    
    df = DataFile( tmp.name )
    
    for data in data_list:
      df.append( data )
    
    self.assertEqual( data_list, list( df ) )
    
    df.selfTest()
    
    df.close()
    
    df = DataFile( tmp.name )
    
    self.assertEqual( data_list, list( df ) )
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    data_list = generateDataList( len(data_list), len(data_list), 77, 157 )
    
    for i in range(0, len(data_list)):
      df[i] = data_list[i]
    
    self.assertEqual( data_list, list( df ) )
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    del df[len(df) - 1]
    del data_list[len(data_list) - 1]
    
    df.selfTest()
    
    del df[len(df) // 2]
    del data_list[len(data_list) // 2]
    
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    data_list = generateDataList( len(data_list), len(data_list), 157, 257 )
    
    indexes = list( range(0, len(data_list) ) )
    random.shuffle( indexes )
    for i in indexes:
      df[i] = data_list[i]
    
    self.assertEqual( data_list, list( df ) )
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    del df[len(df) - 1]
    del data_list[len(data_list) - 1]
    
    df.selfTest()
    
    del df[len(df) // 2]
    del data_list[len(data_list) // 2]
    
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    data_list = generateDataList( len(data_list), len(data_list), 150, 200 )
    
    indexes = list( range(0, len(data_list) ) )
    random.shuffle( indexes )
    for i in indexes:
      df[i] = data_list[i]
    
    self.assertEqual( data_list, list( df ) )
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    del df[len(df) - 1]
    del data_list[len(data_list) - 1]
    
    df.selfTest()
    
    del df[len(df) // 2]
    del data_list[len(data_list) // 2]
    
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    data_list = generateDataList( len(data_list), len(data_list), 1570, 2570 )
    
    indexes = list( range(0, len(data_list) ) )
    random.shuffle( indexes )
    for i in indexes:
      df[i] = data_list[i]
    
    self.assertEqual( data_list, list( df ) )
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    del df[len(df) - 1]
    del data_list[len(data_list) - 1]
    
    df.selfTest()
    
    del df[len(df) // 2]
    del data_list[len(data_list) // 2]
    
    self.assertEqual( data_list, list( df ) )
    df.selfTest()
    
    for i in range(0, len(df) ):
      del df[0]
    
    self.assertEqual( len( df ), 0 )
    self.assertFalse( df )
    df.selfTest()


#//===========================================================================//
