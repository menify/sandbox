import sys
import os.path
import types

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import skip, AqlTestCase, runLocalTests

from aql.values import SimpleValue
from aql.nodes import Node, Builder
from aql.utils import Tempfile, Tempdir,\
  removeUserHandler, addUserHandler, disableDefaultHandlers, enableDefaultHandlers
from aql.main import Project, ProjectConfig, Tool, \
                     ErrorProjectBuilderMethodWithKW, \
                     ErrorProjectBuilderMethodFewArguments, \
                     ErrorProjectBuilderMethodUnbound, \
                     ErrorProjectInvalidMethod

#//===========================================================================//

class TestNullBuilder (Builder):
  
  def   __init__(self, options, v1, v2, v3 ):
    self.v1 = v1
    self.v2 = v2
    self.v3 = v3
  
  #//-------------------------------------------------------//
  
  def   build( self, node ):
    node.setNoTargets()

#//===========================================================================//

class TestTool( Tool ):
  def   Noop( self, options, v1, v2, v3 ):
    return TestNullBuilder( options, v1, v2, v3 )

#//===========================================================================//

class TestProject( AqlTestCase ):
  
  # noinspection PyUnusedLocal
  def   eventNodeBuilding( self, settings, node ):
    self.building_started += 1
  
  #//-------------------------------------------------------//
  
  # noinspection PyUnusedLocal
  def   eventNodeBuildingFinished( self, settings, node, builder_output, progress ):
    self.building_finished += 1
  
  #//-------------------------------------------------------//
  
  def   setUp( self ):
    super(TestProject,self).setUp()
    disableDefaultHandlers()
    
    self.building_started = 0
    addUserHandler( self.eventNodeBuilding )
    
    self.building_finished = 0
    addUserHandler( self.eventNodeBuildingFinished )
  
  #//-------------------------------------------------------//
  
  def   tearDown( self ):
    removeUserHandler( self.eventNodeBuilding )
    removeUserHandler( self.eventNodeBuildingFinished )

    enableDefaultHandlers()
    
    super(TestProject,self).tearDown()
  
  #//-------------------------------------------------------//
  
  def test_prj_config(self):
    
    with Tempfile() as f:
      cfg = b"""
abc = 123
size = 100
options.build_variant = "final"
"""
      f.write( cfg )
      f.flush()
      
      args = ["-v", "-j", 5, "-c", f ]
      cfg = ProjectConfig( args )
      
      self.assertEqual( cfg.options.bv, 'final' )
      self.assertEqual( cfg.jobs, 5 )
      self.assertTrue( cfg.verbose )
  
  #//-------------------------------------------------------//
  
  @skip
  def   test_prj_add_builder( self ):
    cfg = ProjectConfig( [] )
    prj = Project( cfg )
    
    class TestBuilder (Builder):
      def   __init__(self):
        self.signature = b''
      def   build( self, build_manager, vfile, node ):
        return self.nodeTargets( SimpleValue( b"", name = "value1" ) )
    
    class TestTool:
      def   TestBuilder( self, prj, options ):
        pass
      
      def   TestBuilder2( self, prj, options, **vals ):
        pass
      
      def   TestBuilder3( self, prj ):
        pass
      
      def   TestBuildNode( self, prj, options, source ):
        return Node( TestBuilder(), '' )
    
    if isinstance( TestTool.TestBuilder, types.MethodType ):
      self.assertRaises( ErrorProjectBuilderMethodUnbound, prj.AddBuilder, TestTool.TestBuilder )
    
    #~ prj.AddBuilder( TestTool().TestBuilder )
    #~ self.assertRaises( ErrorProjectBuilderMethodResultInvalid, prj.TestBuilder )
    
    self.assertRaises( ErrorProjectBuilderMethodWithKW, prj.AddBuilder, TestTool().TestBuilder2 )
    self.assertRaises( ErrorProjectBuilderMethodFewArguments, prj.AddBuilder, TestTool().TestBuilder3 )
    self.assertRaises( ErrorProjectInvalidMethod, prj.AddBuilder, "TestTool().TestBuilder3" )
    
    prj.AddBuilder( TestTool().TestBuildNode )
    node = prj.TestBuildNode( 'a' )
    #~ self.assertRaises( ErrorProjectBuilderMethodResultInvalid, prj.TestBuilder )
  
  #//-------------------------------------------------------//
  
  def   test_prj_builtin_tools( self ):
    
    with Tempdir() as tmp_dir:
      
      cfg = ProjectConfig( args = [ "build_dir=%s" % tmp_dir] )
      
      prj = Project( cfg.options, cfg.targets )
      
      prj.tools.ExecuteCommand( "python", "-c", "print('test builtin')" )
      prj.Build()
      
      self.assertEqual( self.building_started, 1 )
      self.assertEqual( self.building_finished, 1 )
      
      self.building_started = 0
      
      prj = Project( cfg.options, cfg.targets )
      prj.tools.ExecuteCommand( "python", "-c", "print('test builtin')" )
      prj.Build()
      
      self.assertEqual( self.building_started, 0 )
  
  #//-------------------------------------------------------//
  
  def   test_prj_targets( self ):
    
    with Tempdir() as tmp_dir:
      
      cfg = ProjectConfig( args = [ "build_dir=%s" % tmp_dir, "test"] )
      
      prj = Project( cfg.options, cfg.targets )
      
      cmd = prj.tools.ExecuteCommand( "python", "-c", "print('test builtin')" )
      cmd_other = prj.tools.ExecuteCommand( "python", "-c", "print('test other')" )
      
      prj.Alias('test', cmd )
      prj.Build()
      
      self.assertEqual( self.building_finished, 1 )
  
  #//-------------------------------------------------------//
  
  def   test_prj_default_targets( self ):
    
    with Tempdir() as tmp_dir:
      
      cfg = ProjectConfig( args = [ "build_dir=%s" % tmp_dir] )
      
      prj = Project( cfg.options, cfg.targets )
      
      cmd = prj.tools.ExecuteCommand( "python", "-c", "print('test builtin')" )
      cmd_other = prj.tools.ExecuteCommand( "python", "-c", "print('test other')" )
      cmd_other2 = prj.tools.ExecuteCommand( "python", "-c", "print('test other2')" )
      
      prj.Default( [cmd_other, cmd_other2] )
      prj.Build()
      
      self.assertEqual( self.building_finished, 2 )
  
  #//=======================================================// 
  
  def   test_prj_implicit_value_args( self ):
    
    with Tempdir() as tmp_dir:
      
      cfg = ProjectConfig( args = [ "build_dir=%s" % tmp_dir] )
      
      prj = Project( cfg.options, cfg.targets )
      
      tool = prj.tools.AddTool( TestTool )
      
      tool.Noop( v1 = "a", v2 = "b", v3 = "c" )
      prj.Build()
      
      self.assertEqual( self.building_finished, 1 )
      
      #//-------------------------------------------------------//
      
      self.building_finished = 0
      
      tool.Noop( v1 = "aa", v2 = "bb", v3 = "cc" )
      prj.Build()
      self.assertEqual( self.building_finished, 0 )
      
      #//-------------------------------------------------------//
      
      self.building_finished = 0
      
      v1 = SimpleValue("a", name = "value1")
      
      tool.Noop( v1 = v1, v2 = "b", v3 = "c" )
      prj.Build()
      self.assertEqual( self.building_finished, 1 )
      
      #//-------------------------------------------------------//
      
      self.building_finished = 0
      
      v1 = SimpleValue("ab", name = "value1")
      
      tool.Noop( v1 = v1, v2 = "b", v3 = "c" )
      prj.Build()
      self.assertEqual( self.building_finished, 1 )
      
      #//-------------------------------------------------------//
      
      self.building_finished = 0
      
      v1 = SimpleValue("ab", name = "value1")
      
      tool.Noop( v1 = v1, v2 = "b", v3 = "c" )
      prj.Build()
      self.assertEqual( self.building_finished, 0 )

#//===========================================================================//

if __name__ == "__main__":
  runLocalTests()
