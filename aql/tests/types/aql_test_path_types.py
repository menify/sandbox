import sys
import os.path

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import AqlTestCase, runLocalTests

from aql.util_types import FilePath

try:
  _splitunc = os.path.splitunc
except AttributeError:
  def _splitunc( path ):
    return str(), path

#//===========================================================================//

class TestPathTypes( AqlTestCase ):
  #//===========================================================================//

  def test_file_path(self):
    
    file1 = os.path.abspath('foo/file.txt')
    file2 = os.path.abspath('bar/file2.txt')
    
    p = FilePath( file1 )
    self.assertEqual( p.filename(), os.path.basename(file1) )
    self.assertEqual( p.dirname(), os.path.dirname(file1) )
    self.assertEqual( p.name(), os.path.splitext( os.path.basename(file1) )[0] )
    self.assertEqual( p.ext(), os.path.splitext( os.path.basename(file1) )[1] )
    self.assertIn( p.drive(), [ os.path.splitdrive( file1 )[0], _splitunc( file1 )[0] ] )
    
    self.assertEqual( p.change( ext = '.ttt', dirname = 'test', name = 'test_file', prefix = '_'), os.path.join( 'test', '_test_file.ttt' ) )
    
    self.assertEqual( FilePath('foo/bar').join( 'foo/file.txt' ).normpath(), os.path.normpath( 'foo/bar/foo/file.txt' ) )
    self.assertEqual( FilePath('foo/bar').join( 'foo', 'file.txt' ).normpath(), os.path.normpath( 'foo/bar/foo/file.txt') )
    self.assertEqual( FilePath('foo/bar').join( 'foo', 'foo2', 'test', 'file.txt' ).normpath(), os.path.normpath( 'foo/bar/foo/foo2/test/file.txt' ) )
    
#//===========================================================================//

if __name__ == "__main__":
  runLocalTests()
