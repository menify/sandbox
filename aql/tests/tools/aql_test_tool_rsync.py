import os
import sys

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import skip, AqlTestCase, runLocalTests

from aql.utils import Tempfile, Tempdir
from aql.values import ValuesFile
from aql.nodes import Node, BuildManager
from aql.options import builtinOptions

from aql.main import Project, ProjectConfig

import rsync

#//===========================================================================//

def   _build( prj ):
  if not prj.Build( verbose = True ):
    prj.build_manager.printFails()
    assert False, "Build failed"

#//===========================================================================//

class TestToolRsync( AqlTestCase ):
  
  def test_rsync_push_local(self):
    with Tempdir() as tmp_dir:
      with Tempdir() as src_dir:
        with Tempdir() as target_dir:
          src_files = self.generateCppFiles( src_dir, "src_test", 3 )
          
          cfg = ProjectConfig( args = [ "build_dir=%s" % tmp_dir] )
          
          prj = Project( cfg.options, cfg.targets )
          
          prj.tools.rsync.Push( src_files, target = target_dir )
          
          _build( prj )
          
          prj.tools.rsync.Push( src_files, target = target_dir )
          
          _build( prj )
  
  #//=======================================================//

  def test_rsync_push_remote(self):
    with Tempdir() as tmp_dir:
      with Tempdir() as src_dir:
        src_files = self.generateCppFiles( src_dir, "src_test", 3 )

        cfg = ProjectConfig( args = [ "build_dir=%s" % tmp_dir] )

        prj = Project( cfg.options, cfg.targets )

        remote_files = prj.tools.rsync.Push( src_files, target = 'test_rsync_push',
                                             host = 'nas', key_file = r'C:\cygwin\home\me\rsync.key',
                                             exclude="*.h" )
        remote_files.options.rsync_flags += ['--chmod=u+rw,g+r,o+r']
        remote_files.options.rsync_flags += ['--delete-excluded']
        _build( prj )


  #//=======================================================//

  def test_rsync_pull(self):
    with Tempdir() as tmp_dir:
      with Tempdir() as src_dir:
        with Tempdir() as target_dir:
          src_files = self.generateCppFiles( src_dir, "src_test", 3 )
          
          cfg = ProjectConfig( args = [ "build_dir=%s" % tmp_dir] )
          
          prj = Project( cfg.options, cfg.targets )
          
          prj.tools.rsync.Pull( src_files, target = target_dir )
          
          _build( prj )
          
          prj.tools.rsync.Pull( src_files, target = target_dir )
          
          _build( prj )
  
  #//=======================================================//
    
  @skip
  def test_rsync_get(self):
    
    with Tempdir() as tmp_dir:
      
      options = builtinOptions()
      options.update( rsyncOptions() )
      
      options.env['PATH'] += r"C:\cygwin\bin"
      options.rsync_cygwin = True
      
      rsync = RSyncGetBuilder( options, local_path = 'D:\\test1_local\\', remote_path = 'D:\\test1\\' )
      
      vfilename = Tempfile( dir = str(tmp_dir), suffix = '.aql.values' )
      
      bm = BuildManager( vfilename, 4, True )
      vfile = ValuesFile( vfilename )
      try:
        rsync_files = Node( rsync, [] )
        self.assertFalse( rsync_files.isActual( vfile ) )
        
        bm.add( rsync_files )
        bm.build()
        
        rsync_files = Node( rsync, [] )
        self.assertTrue( rsync_files.isActual( vfile ) )
      
      finally:
        vfile.close()
        bm.close()
  
  #//-------------------------------------------------------//
  
  @skip
  def test_rsync_put(self):
    
    with Tempdir() as tmp_dir:
      
      options = builtinOptions()
      options.update( rsyncOptions() )
      
      options.env['PATH'] += r"C:\cygwin\bin"
      options.rsync_cygwin = True
      
      rsync = RSyncPutBuilder( options, local_path = 'D:\\test1_local\\', remote_path = 'D:\\test1\\', exclude = [".svn", "test_*"] )
      
      vfilename = Tempfile( dir = str(tmp_dir), suffix = '.aql.values' )
      
      bm = BuildManager( vfilename, 4, True )
      vfile = ValuesFile( vfilename )
      try:
        rsync_files = Node( rsync, [] )
        self.assertFalse( rsync_files.isActual( vfile ) )
        
        bm.add( rsync_files )
        bm.build()
        
        rsync_files = Node( rsync, [] )
        self.assertTrue( rsync_files.isActual( vfile ) )
        
        sync_files  = [ r'd:\test1_local\sbe\sbe\list\list.hpp',
                        r'd:\test1_local\sbe\sbe\path_finder\path_finder.hpp',
                      ]
        
        rsync_files = Node( rsync, sync_files )
        self.assertFalse( rsync_files.isActual( vfile ) )
        bm.add( rsync_files )
        bm.build()
        
        rsync_files = Node( rsync, sync_files )
        self.assertTrue( rsync_files.isActual( vfile ) )
        bm.add( rsync_files )
        bm.build()
      
      finally:
        vfile.close()
        bm.close()

#//===========================================================================//

if __name__ == "__main__":
  runLocalTests()
