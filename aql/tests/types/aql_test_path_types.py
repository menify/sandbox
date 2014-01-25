import sys
import os.path

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import AqlTestCase, runLocalTests

from aql.util_types import FilePath, FilePaths

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
    host_file = '//host/share/bar/file3.txt'
    
    
    disk_file = ''
    if file1[0].isalpha():
      disk_file = os.path.join( 'a:', os.path.splitdrive( file1 )[1] )
    
    p = FilePath( file1 )
    p2 = FilePath( file2 )
    self.assertEqual( p.filename(), os.path.basename(file1) )
    self.assertEqual( p.dirname(), os.path.dirname(file1) )
    self.assertEqual( p.name(), os.path.splitext( os.path.basename(file1) )[0] )
    self.assertEqual( p.ext(), os.path.splitext( os.path.basename(file1) )[1] )
    self.assertIn( p.drive(), [ os.path.splitdrive( file1 )[0], _splitunc( file1 )[0] ] )
    
    self.assertEqual( p.joinFromCommon( p2 ), os.path.join( p, os.path.basename(p2.dirname()), p2.filename() ) )
    self.assertEqual( p.joinFromCommon( host_file ), os.path.join( p, *(filter(None, host_file.split('/'))) ) )
    
    if disk_file:
      self.assertEqual( p.joinFromCommon( disk_file ), os.path.join( p, 'a', os.path.splitdrive( file1 )[1].strip( os.path.sep ) ) )
    self.assertEqual( p.joinFromCommon( '' ), file1 )
    self.assertEqual( p.joinFromCommon( '.' ), file1 )
    self.assertEqual( p.joinFromCommon( '..' ), p.dirname() )
    self.assertEqual( FilePath('foo/bar').joinFromCommon( 'bar/foo/file.txt' ), 'foo/bar/bar/foo/file.txt' )
    self.assertEqual( FilePath('foo/bar').joinFromCommon( 'foo/file.txt' ), 'foo/bar/file.txt' )
    
    self.assertEqual( FilePath('foo/bar').join( 'foo/file.txt' ), 'foo/bar/foo/file.txt' )
    self.assertEqual( FilePath('foo/bar').join( 'foo', 'file.txt' ), 'foo/bar/foo/file.txt' )
    self.assertEqual( FilePath('foo/bar').join( 'foo', 'foo2', 'test', 'file.txt' ), 'foo/bar/foo/foo2/test/file.txt' )
  
  #//=======================================================//
  
  def   test_file_paths( self ):
    paths = FilePaths()
    
    paths += ['file0.txt', 'file1.txt', 'file2.txt' ]
    
    self.assertEqual( paths.change( ext = '.ttt'), ['file0.ttt', 'file1.ttt', 'file2.ttt' ] )
    self.assertEqual( paths.change( dirname = 'foo/bar'), ['foo/bar/file0.txt', 'foo/bar/file1.txt', 'foo/bar/file2.txt' ] )
  
  #//=======================================================//
  
  def   test_file_path_groups( self ):
    paths = FilePaths(['abc/file0.txt', 'abc/file1.txt', 'def/file2.txt', 'ghi/file0.txt', 'klm/file0.txt', 'ghi/file1.txt' ])
    
    groups = paths.groupUniqueNames()
    
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt', 'def/file2.txt'], ['ghi/file0.txt', 'ghi/file1.txt'], ['klm/file0.txt'] ])
    
    groups = paths.groupUniqueNames( max_group_size = 1 )
    
    self.assertEqual( groups, [ ['abc/file0.txt'], ['abc/file1.txt'], ['def/file2.txt'], ['ghi/file0.txt'], ['klm/file0.txt'], ['ghi/file1.txt' ] ])
    
    groups = paths.groupUniqueNames( max_group_size = 2 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt'], ['def/file2.txt', 'ghi/file0.txt'], ['klm/file0.txt', 'ghi/file1.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 3 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt'], ['def/file2.txt', 'ghi/file0.txt'], ['klm/file0.txt', 'ghi/file1.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 2 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt', 'def/file2.txt'], ['ghi/file0.txt','ghi/file1.txt'], ['klm/file0.txt'] ])
    
    paths = FilePaths(['abc/file0.txt', 'abc/file1.txt', 'def/file2.txt', 'ghi/file3.txt', 'klm/file4.txt', 'ghi/file5.txt', 'ghi/file6.txt' ])
    groups = paths.groupUniqueNames( wish_groups = 2 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt', 'def/file2.txt'], ['ghi/file3.txt', 'klm/file4.txt', 'ghi/file5.txt', 'ghi/file6.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 1 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt', 'def/file2.txt', 'ghi/file3.txt', 'klm/file4.txt', 'ghi/file5.txt', 'ghi/file6.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 3 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt'], ['def/file2.txt', 'ghi/file3.txt'], ['klm/file4.txt', 'ghi/file5.txt', 'ghi/file6.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 4 )
    self.assertEqual( groups, [ ['abc/file0.txt'], ['abc/file1.txt', 'def/file2.txt'], ['ghi/file3.txt', 'klm/file4.txt'], ['ghi/file5.txt', 'ghi/file6.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 5 )
    self.assertEqual( groups, [ ['abc/file0.txt'], ['abc/file1.txt'], ['def/file2.txt'], ['ghi/file3.txt', 'klm/file4.txt'], ['ghi/file5.txt', 'ghi/file6.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 6 )
    self.assertEqual( groups, [ ['abc/file0.txt'], ['abc/file1.txt'], ['def/file2.txt'], ['ghi/file3.txt'], ['klm/file4.txt'], ['ghi/file5.txt', 'ghi/file6.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 7 )
    self.assertEqual( groups, [ ['abc/file0.txt'], ['abc/file1.txt'], ['def/file2.txt'], ['ghi/file3.txt'], ['klm/file4.txt'], ['ghi/file5.txt'], ['ghi/file6.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 8 )
    self.assertEqual( groups, [ ['abc/file0.txt'], ['abc/file1.txt'], ['def/file2.txt'], ['ghi/file3.txt'], ['klm/file4.txt'], ['ghi/file5.txt'], ['ghi/file6.txt' ] ])
    
    groups = paths.groupUniqueNames( wish_groups = 10 )
    self.assertEqual( groups, [ ['abc/file0.txt'], ['abc/file1.txt'], ['def/file2.txt'], ['ghi/file3.txt'], ['klm/file4.txt'], ['ghi/file5.txt'], ['ghi/file6.txt' ] ])
    
    paths = FilePaths(['file0.txt', 'file1.txt', 'file2.txt', 'file3.txt', 'file4.txt'])
    groups = paths.groupUniqueNames( wish_groups = 4 )
    self.assertEqual( groups, [ ['file0.txt'], ['file1.txt'], ['file2.txt'], ['file3.txt', 'file4.txt'] ] )
  
  #//=======================================================//
  
  def   test_file_path_group_dirs( self ):
    paths = FilePaths(['abc/file0.txt', 'abc/file1.txt', 'def/file2.txt', 'ghi/file0.txt', 'klm/file0.txt', 'ghi/file1.txt' ])
    
    groups, indexes = paths.groupByDir()
    
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt'], ['def/file2.txt'], ['ghi/file0.txt', 'ghi/file1.txt'], ['klm/file0.txt'] ])
    self.assertEqual( indexes, [ [0,1], [2], [3,5], [4] ])
    
    groups, indexes = paths.groupByDir( max_group_size = 1 )
    
    self.assertEqual( groups, [ ['abc/file0.txt'], ['abc/file1.txt'], ['def/file2.txt'], ['ghi/file0.txt'], ['ghi/file1.txt' ], ['klm/file0.txt'] ] )
    
    groups, indexes = paths.groupByDir( max_group_size = 2 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt'], ['def/file2.txt'], ['ghi/file0.txt', 'ghi/file1.txt'], ['klm/file0.txt'] ])
    
    groups, indexes = paths.groupByDir( wish_groups = 3 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt'], ['def/file2.txt'], ['ghi/file0.txt', 'ghi/file1.txt'], ['klm/file0.txt'] ])
    
    paths = FilePaths(['abc/file0.txt', 'abc/file1.txt', 'abc/file2.txt', 'abc/file3.txt', 'abc/file4.txt', 'abc/file5.txt' ])
    groups, indexes = paths.groupByDir( wish_groups = 3 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt'], ['abc/file2.txt', 'abc/file3.txt'], ['abc/file4.txt', 'abc/file5.txt'] ])
    
    groups, indexes = paths.groupByDir( wish_groups = 2 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt', 'abc/file2.txt'], ['abc/file3.txt', 'abc/file4.txt', 'abc/file5.txt'] ])
    
    groups, indexes = paths.groupByDir( wish_groups = 2, max_group_size = 1 )
    self.assertEqual( groups, [ ['abc/file0.txt'], ['abc/file1.txt'], ['abc/file2.txt'], ['abc/file3.txt'], ['abc/file4.txt'], ['abc/file5.txt'] ])
    
    groups, indexes = paths.groupByDir( wish_groups = 1 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt', 'abc/file2.txt', 'abc/file3.txt', 'abc/file4.txt', 'abc/file5.txt'] ])
    
    paths = FilePaths(['abc/file0.txt', 'abc/file1.txt', 'abc/file2.txt', 'abc/file3.txt', 'abc/file4.txt', 'abc/file5.txt', 'abc/file6.txt' ])
    groups, indexes = paths.groupByDir( wish_groups = 3 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt'], ['abc/file2.txt', 'abc/file3.txt'], ['abc/file4.txt', 'abc/file5.txt', 'abc/file6.txt'] ])
    
    groups, indexes = paths.groupByDir( wish_groups = 3, max_group_size = 2 )
    self.assertEqual( groups, [ ['abc/file0.txt', 'abc/file1.txt'], ['abc/file2.txt', 'abc/file3.txt'], ['abc/file4.txt', 'abc/file5.txt'], ['abc/file6.txt'] ])

    
  #//=======================================================//
  
  def   test_file_path_change( self ):
    paths = FilePaths(['abc/file0.txt', 'abc/file1.txt', 'def/file2.txt'])
    paths_ttt, paths_eee = paths.change( ext = ['.ttt', '.eee'])
    
    self.assertEqual( paths_ttt, ['abc/file0.ttt', 'abc/file1.ttt', 'def/file2.ttt'])
    self.assertEqual( paths_eee, ['abc/file0.eee', 'abc/file1.eee', 'def/file2.eee'])
    
    paths_foo, paths_bar = paths.change( dirname = ['foo', 'bar'] )
    
    self.assertEqual( paths_foo, ['foo/file0.txt', 'foo/file1.txt', 'foo/file2.txt'])
    self.assertEqual( paths_bar, ['bar/file0.txt', 'bar/file1.txt', 'bar/file2.txt'])
    
    paths_foo_ttt, paths_foo_eee, paths_bar_ttt, paths_bar_eee = paths.change( dirname = ['foo', 'bar'], ext = ['.ttt', '.eee'] )
    
    self.assertEqual( paths_foo_ttt, ['foo/file0.ttt', 'foo/file1.ttt', 'foo/file2.ttt'])
    self.assertEqual( paths_foo_eee, ['foo/file0.eee', 'foo/file1.eee', 'foo/file2.eee'])
    self.assertEqual( paths_bar_ttt, ['bar/file0.ttt', 'bar/file1.ttt', 'bar/file2.ttt'])
    self.assertEqual( paths_bar_eee, ['bar/file0.eee', 'bar/file1.eee', 'bar/file2.eee'])
    
    paths_www = paths.change( ext = '.www' )
    self.assertEqual( paths_www, ['abc/file0.www', 'abc/file1.www', 'def/file2.www'])
  
  #//=======================================================//
  
  def   test_file_path_add( self ):
    paths = FilePaths(['abc/file0.txt', 'abc/file1.txt', 'def/file2.txt'])
    paths_ttt, paths_eee = paths.add( suffix = ['.ttt', '.eee'] )
    
    self.assertEqual( paths_ttt, ['abc/file0.txt.ttt', 'abc/file1.txt.ttt', 'def/file2.txt.ttt'])
    self.assertEqual( paths_eee, ['abc/file0.txt.eee', 'abc/file1.txt.eee', 'def/file2.txt.eee'])
    
    paths_www = paths.add( suffix = '.www' )
    self.assertEqual( paths_www, ['abc/file0.txt.www', 'abc/file1.txt.www', 'def/file2.txt.www'])
  
#//===========================================================================//

if __name__ == "__main__":
  runLocalTests()
