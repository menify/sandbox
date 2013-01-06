﻿import sys
import os.path
import timeit
import hashlib
import shutil

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import skip, AqlTestCase, runLocalTests

from aql.nodes import Node, Builder
from aql.utils import Tempfile
from aql.main import Project, ProjectConfig, \
                     ErrorProjectBuilderMethodResultInvalid, \
                     ErrorProjectBuilderMethodExists, \
                     ErrorProjectBuilderMethodWithKW, \
                     ErrorProjectBuilderMethodFewArguments, \
                     ErrorProjectBuilderMethodUnbound, \
                     ErrorProjectInvalidMethod

#//===========================================================================//

class   GccSpecs( object ):
  
  __slots__ = ('version', 'target' )
  
  def   __init__( self, gcc ):
    import re
    from aql.utils import execCommand
    from aql.types import Version
    
    result = execCommand( [gcc, '-v'] )
    
    target_re = re.compile( r'^\s*Target:\s+(.+)$', re.MULTILINE )
    version_re = re.compile( r'^\s*gcc version\s+(.+)$', re.MULTILINE )
    
    out = result.err
    
    match = target_re.search( out )
    self.target = match.group(1).strip() if match else ''
    
    match = version_re.search( out )
    self.version = Version( match.group(1).strip() if match else '' )
    

#//===========================================================================//

class TestProject( AqlTestCase ):
  
  def   test_gcc_specs( self ):
    specs = GccSpecs( 'gcc' )
    print( specs.version )
    print( specs.target )
  
  #//-------------------------------------------------------//
  
  def test_prj_config(self):
    
    args = "-v".split()
    
    with Tempfile() as f:
      cfg = b"""
abc = 123
size = 100
keep_going = True
jobs=5
options.build_variant = "final"
"""
      f.write( cfg )
      f.flush()
    
      cfg = ProjectConfig( args )
      cfg.readConfig( f.name )
    
    prj = Project( cfg )
    
    self.assertEqual( prj.options.bv, 'final' )
    self.assertEqual( prj.config.jobs, 5 )
  
  #//-------------------------------------------------------//
  
  def   test_prj_add_builder( self ):
    cfg = ProjectConfig( [] )
    prj = Project( cfg )
    
    
    class TestBuilder (Builder):
      def   __init__(self):
        self.signature = b''
      def   build( self, build_manager, vfile, node ):
        return self.nodeTargets( Value( "value1", b"" ) )
    
    class TestTool:
      def   TestBuilder( self, prj, options ):
        pass
      
      def   TestBuilder2( self, prj, options, **vals ):
        pass
      
      def   TestBuilder3( self, prj ):
        pass
      
      def   TestBuildNode( self, prj, options, source ):
        return Node( TestBuilder(), '' )
    
    self.assertRaises( ErrorProjectBuilderMethodUnbound, prj.AddBuilder, TestTool.TestBuilder )
    
    prj.AddBuilder( TestTool().TestBuilder )
    self.assertRaises( ErrorProjectBuilderMethodResultInvalid, prj.TestBuilder )
    
    self.assertRaises( ErrorProjectBuilderMethodExists, prj.AddBuilder, TestTool().TestBuilder )
    self.assertRaises( ErrorProjectBuilderMethodWithKW, prj.AddBuilder, TestTool().TestBuilder2 )
    self.assertRaises( ErrorProjectBuilderMethodFewArguments, prj.AddBuilder, TestTool().TestBuilder3 )
    self.assertRaises( ErrorProjectInvalidMethod, prj.AddBuilder, "TestTool().TestBuilder3" )
    
    prj.AddBuilder( TestTool().TestBuildNode )
    node = prj.TestBuildNode( 'a' )
    self.assertRaises( ErrorProjectBuilderMethodResultInvalid, prj.TestBuilder )
    

#//===========================================================================//

if __name__ == "__main__":
  runLocalTests()
