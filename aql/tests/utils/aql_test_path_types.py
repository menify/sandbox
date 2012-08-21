﻿import sys
import os.path
import timeit

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import skip, AqlTestCase, runLocalTests

from aql_event_manager import event_manager
from aql_event_handler import EventHandler
from aql_path_types import FilePath, FilePaths

#//===========================================================================//

class TestPathTypes( AqlTestCase ):
  #//===========================================================================//

  def test_file_path(self):
    
    file1 = os.path.abspath('foo/file.txt')
    file2 = os.path.abspath('bar/file2.txt')
    host_file = '//host/share/bar/file3.txt'
    
    if file1[0].isalpha():
      disk_file = os.path.join( 'a:', os.path.splitdrive( file1 )[1] )
    
    p = FilePath( file1 )
    p2 = FilePath( file2 )
    self.assertEqual( p.name_ext, os.path.basename(file1) )
    self.assertEqual( p.dir, os.path.dirname(file1) )
    self.assertEqual( p.name, os.path.splitext( os.path.basename(file1) )[0] )
    self.assertEqual( p.ext, os.path.splitext( os.path.basename(file1) )[1] )
    self.assertEqual( p.drive, os.path.splitdrive( file1 )[0] )
    
    self.assertEqual( p.mergePaths( p2 ), os.path.join( p, os.path.basename(p2.dir), p2.name_ext ) )
    self.assertEqual( p.mergePaths( host_file ), os.path.join( p, *(filter(None, host_file.split('/'))) ) )
    
    self.assertEqual( p.mergePaths( disk_file ), os.path.join( p, 'a', os.path.splitdrive( file1 )[1].strip( os.path.sep ) ) )
    self.assertEqual( p.mergePaths( '' ), file1 )
    self.assertEqual( p.mergePaths( '.' ), file1 )
    self.assertEqual( p.mergePaths( '..' ), p.dir )
    self.assertEqual( FilePath('foo/bar').mergePaths( 'bar/foo/file.txt' ), 'foo/bar/bar/foo/file.txt' )
    self.assertEqual( FilePath('foo/bar').mergePaths( 'foo/file.txt' ), 'foo/bar/file.txt' )
  
  #//=======================================================//
  
  def   test_file_paths( self ):
    paths = FilePaths()
    
    paths += map( os.path.abspath, ['file0.txt', 'file1.txt', 'file2.txt' ] )
    
    print( paths.replaceExt('.ttt') )
    print( paths.replaceDir('foo/bar') )
  
#//===========================================================================//

if __name__ == "__main__":
  runLocalTests()
