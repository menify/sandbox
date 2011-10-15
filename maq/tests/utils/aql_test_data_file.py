
import os
import sys
import random

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import testcase, skip, runTests
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
      df.append( data ); df.selfTest()
    
    self.assertEqual( data_list, list( df ) )
    
    df.selfTest()
    
    df.close()
    
    df = DataFile( tmp.name )
    
    self.assertEqual( data_list, list( df ) )
    df.selfTest()
    
    df[-1] = bytearray( len(df[-1]) // 2 )
    df.selfTest()
    
    df[0] = bytearray( len(df[0]) // 2 )
    df.selfTest()
    
    df[2] = bytearray( len(df[2]) // 2 )
    df.selfTest()
    
    df[-1] = bytearray( len(df[-1]) * 8 )
    df.selfTest()
    
    df[0] = bytearray( len(df[0]) * 8 )
    df.selfTest()
    
    df[2] = bytearray( len(df[2]) * 8 )
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    data_list = generateDataList( len(data_list), len(data_list), 77, 157 )
    
    for i in range(0, len(data_list)):
      df[i] = data_list[i]
    
    self.assertEqual( data_list, list( df ) )
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    del df[-1]
    del data_list[-1]
    
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
      df.selfTest()
    
    self.assertEqual( data_list, list( df ) )
    df.selfTest()
    
    #//-------------------------------------------------------//
    
    del df[-1]
    del data_list[-1]
    
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
    
    del df[-1]
    del data_list[-1]
    
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
    
    del df[0]
    del data_list[0]
    
    df.selfTest()
    
    del df[-1]
    del data_list[-1]
    
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

@testcase
def   test_data_file_update(self):
  with Tempfile() as tmp:
    
    data_list = generateDataList( 50, 50, 7, 57 )
    
    df = DataFile( tmp.name )
    
    for data in data_list:
      df.append( data ); df.selfTest()
    
    self.assertEqual( data_list, list( df ) )
    
    df.selfTest()
    
    self.assertEqual( df.update(), [] )
    
    df2 = DataFile( tmp.name ); df2.selfTest()
    df2[ 1 ] = bytearray( 3 ); df2.selfTest()
    df2[ 2 ] = bytearray( 3 ); df2.selfTest()
    df2.append( bytearray( 4 ) ); df2.selfTest()
    df2.append( bytearray( 4 ) ); df2.selfTest()
    
    self.assertEqual( df.update(), [1,2, len(df2) - 2, len(df2) - 1] )
    df.selfTest()


#//===========================================================================//

if __name__ == "__main__":
  runTests()
