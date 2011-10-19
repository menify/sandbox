import os
import sys
import random

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import testcase, skip, runTests
from aql_temp_file import Tempfile
from aql_data_file import DataFile

#//===========================================================================//

def   generateData( min_size, max_size ):
  return bytearray( random.randint( min_size, max_size ) )

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
    
    data_list = generateDataList( 3, 3, 7, 57 )
    data_hash = {}
    
    df = DataFile( tmp.name )
    
    for data in data_list:
      key = df.append( data ); df.selfTest()
      data_hash[ key ] = data
    
    self.assertEqual( data_hash, dict( df ) )
    
    df.close(); df.selfTest()
    
    df = DataFile( tmp.name ); df.selfTest()
    
    self.assertEqual( data_hash, dict( df ) )
    
    for key in data_hash:
      data = bytearray( len(df[key]) )
      df[key] = data
      data_hash[key] = data
      df.selfTest()
    
    self.assertEqual( data_hash, dict( df ) )
    
    for key in data_hash:
      data = bytearray( len(df[key]) // 2 )
      df[key] = data
      data_hash[key] = data
      df.selfTest()
    
    self.assertEqual( data_hash, dict( df ) )
    
    for key in data_hash:
      data = bytearray( len(df[key]) * 8 )
      df[key] = data
      data_hash[key] = data
      df.selfTest()
    
    self.assertEqual( data_hash, dict( df ) )
    
    for key in tuple(data_hash):
      del df[key]
      del data_hash[key]
      df.selfTest()
    
    self.assertEqual( data_hash, dict( df ) )
    
    #//-------------------------------------------------------//
    
    self.assertEqual( len( df ), 0 )
    self.assertFalse( df )

#//===========================================================================//

@skip
@testcase
def   test_data_file_update(self):
  with Tempfile() as tmp:
    
    data_list = generateDataList( 5, 5, 7, 57 )
    
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
    self.assertEqual( df2.update(), [] )
    df2.selfTest()
    
    df3 = DataFile( tmp.name ); df3.selfTest()
    del df3[ 1 ]; df3.selfTest()
    del df3[ 3 ]; df3.selfTest()
    
    self.assertEqual( df.update(), [1, 2, 3, 4] )
    df.selfTest()
    
    self.assertEqual( df2.update(), [1, 2, 3, 4] )
    df2.selfTest()
    
    del df3[ -1 ]; df3.selfTest()
    
    self.assertEqual( df2.update(), [] )
    df2.selfTest()


#//===========================================================================//

if __name__ == "__main__":
  runTests()
