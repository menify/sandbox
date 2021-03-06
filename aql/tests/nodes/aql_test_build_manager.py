import sys
import os.path

sys.path.insert( 0, os.path.normpath(os.path.join( os.path.dirname( __file__ ), '..') ))

from aql_tests import skip, AqlTestCase, runLocalTests

from aql.utils import fileChecksum, Tempdir, \
  disableDefaultHandlers, enableDefaultHandlers, addUserHandler, removeUserHandler

from aql.values import SimpleValue, FileChecksumValue
from aql.options import builtinOptions
from aql.nodes import Node, BatchNode, Builder, FileBuilder, BuildManager
from aql.nodes.aql_build_manager import ErrorNodeDependencyCyclic, ErrorNodeSignatureDifferent

#//===========================================================================//

class CopyValueBuilder (Builder):
  
  def   __init__(self, options ):
    self.signature = b''
  
  def   build( self, node ):
    target_values = []
    
    for source_value in node.getSourceValues():
      copy_value = SimpleValue( source_value.get(), name = source_value.name + '_copy' )
      target_values.append( copy_value )
    
    node.addTargets( target_values )
  
  def   getTraceTargets( self, node, brief ):
    return tuple( value.name for value in node.getTargetValues() )
  
  def   getTraceSources( self, node, brief ):
    return tuple( value.name for value in node.getSourceValues() )


#//===========================================================================//

class ChecksumBuilder (FileBuilder):
  
  NAME_ATTRS = ('replace_ext',)
  SIGNATURE_ATTRS = ('offset', 'length')
  
  def   __init__(self, options, offset, length, replace_ext = False ):
    
    self.offset = offset
    self.length = length
    self.replace_ext = replace_ext
  
  #//-------------------------------------------------------//
  
  def   _buildSrc( self, src, alg ):
    chcksum = fileChecksum( src, self.offset, self.length, alg )
    if self.replace_ext:
      chcksum_filename = os.path.splitext(src)[0]
    else:
      chcksum_filename = src
    
    chcksum_filename += '.%s.chksum' % alg
    
    chcksum_filename = self.getFileBuildPath( chcksum_filename )
    
    with open( chcksum_filename, 'wb' ) as f:
      f.write( chcksum.digest() )
    
    return self.makeFileValue( chcksum_filename, tags = alg )
  
  #//-------------------------------------------------------//
  
  def   build( self, node ):
    target_values = []
    
    for src in node.getSources():
      target_values.append( self._buildSrc( src, 'md5' ) )
      target_values.append( self._buildSrc( src, 'sha512' ) )
    
    node.addTargets( target_values )
  
  #//-------------------------------------------------------//
  
  def   buildBatch( self, node ):
    for src_value in node.getSourceValues():
      targets = [ self._buildSrc( src_value.get(), 'md5' ),
                  self._buildSrc( src_value.get(), 'sha512' ) ]
      
      node.addSourceTargets( src_value, targets )

#//===========================================================================//

class ChecksumSingleBuilder (ChecksumBuilder):
  
  split = ChecksumBuilder.splitSingle

#//===========================================================================//

def   _addNodesToBM( builder, src_files, Node = Node ):
  bm = BuildManager()
  try:
    checksums_node = Node( builder, src_files )
    checksums_node2 = Node( builder, checksums_node )
    
    bm.add( checksums_node ); bm.selfTest()
    bm.add( checksums_node2 ); bm.selfTest()
  except Exception:
    bm.close()
    raise
  
  return bm

#//===========================================================================//

def   _build( bm ):
  try:
    bm.selfTest()
    success = bm.build( jobs = 1, keep_going = False )
    bm.selfTest()
    if not success:
      bm.printFails()
      raise Exception("Nodes failed")
    
  finally:
    bm.close()
    bm.selfTest()

#//===========================================================================//

def   _buildChecksums( builder, src_files, Node = Node ):
  
  bm = _addNodesToBM( builder, src_files, Node )
  _build( bm )

#//===========================================================================//

class TestBuildManager( AqlTestCase ):
  
  def   eventNodeBuilding( self, settings, node ):
    self.building_nodes += 1
  
  #//-------------------------------------------------------//
  
  def   eventNodeBuildingFinished( self, settings, node, builder_output, progress ):
    self.finished_nodes += 1
  
  #//-------------------------------------------------------//
  
  def   eventNodeActual( self, settings, node, progress ):
    self.actual_nodes += 1
  
  #//-------------------------------------------------------//
  
  def   eventNodeOutdated( self, settings, node, progress ):
    self.outdated_nodes += 1
  
  #//-------------------------------------------------------//
  
  def   eventNodeRemoved( self, settings, node, progress ):
    self.removed_nodes += 1
  
  #//-------------------------------------------------------//
  
  def   setUp( self ):
    super(TestBuildManager,self).setUp()
    
    # disableDefaultHandlers()
    
    self.building_nodes = 0
    addUserHandler( self.eventNodeBuilding )
    
    self.finished_nodes = 0
    addUserHandler( self.eventNodeBuildingFinished )
    
    self.actual_nodes = 0
    addUserHandler( self.eventNodeActual )
    
    self.outdated_nodes = 0
    addUserHandler( self.eventNodeOutdated )
    
    self.removed_nodes = 0
    addUserHandler( self.eventNodeRemoved )
  
  #//-------------------------------------------------------//
  
  def   tearDown( self ):
    removeUserHandler( [  self.eventNodeBuilding,
                          self.eventNodeBuildingFinished,
                          self.eventNodeOutdated,
                          self.eventNodeActual,
                          self.eventNodeRemoved,
                      ] )

    enableDefaultHandlers()
    
    super(TestBuildManager,self).tearDown()
  
  #//-------------------------------------------------------//
  
  def test_bm_deps(self):
    
    bm = BuildManager()
    
    value1 = SimpleValue( "http://aql.org/download1", name = "target_url1" )
    value2 = SimpleValue( "http://aql.org/download2", name = "target_url2" )
    value3 = SimpleValue( "http://aql.org/download3", name = "target_url3" )
    
    options = builtinOptions()
    
    builder = CopyValueBuilder( options )
    
    node0 = Node( builder, value1 )
    node1 = Node( builder, node0 )
    node2 = Node( builder, node1 )
    node3 = Node( builder, value2 )
    node4 = Node( builder, value3 )
    node5 = Node( builder, node4 )
    
    node6 = Node( builder, node5 )
    node6.depends( [node0, node1] )
    
    bm.add( node0 ); bm.selfTest(); self.assertEqual( len(bm), 1 )
    bm.add( node1 ); bm.selfTest(); self.assertEqual( len(bm), 2 )
    bm.add( node2 ); bm.selfTest(); self.assertEqual( len(bm), 3 )
    bm.add( node3 ); bm.selfTest(); self.assertEqual( len(bm), 4 )
    bm.add( node4 ); bm.selfTest(); self.assertEqual( len(bm), 5 )
    bm.add( node5 ); bm.selfTest(); self.assertEqual( len(bm), 6 )
    bm.add( node6 ); bm.selfTest(); self.assertEqual( len(bm), 7 )
    
    node0.depends( node3 ); bm.depends( node0, node3 ); bm.selfTest()
    node1.depends( node3 ); bm.depends( node1, node3 ); bm.selfTest()
    node2.depends( node3 ); bm.depends( node2, node3 ); bm.selfTest()
    node3.depends( node4 ); bm.depends( node3, node4 ); bm.selfTest()
    node0.depends( node5 ); bm.depends( node0, node5 ); bm.selfTest()
    node5.depends( node3 ); bm.depends( node5, node3 ); bm.selfTest()
    
    with self.assertRaises(ErrorNodeDependencyCyclic):
      node4.depends( node3 ); bm.depends( node4, node3 ); bm.selfTest()
  
  #//-------------------------------------------------------//
  
  def test_bm_build(self):
    
    with Tempdir() as tmp_dir:
      
      options = builtinOptions()
      options.build_dir = tmp_dir
      
      src_files = self.generateSourceFiles( tmp_dir, 5, 201 )
      
      builder = ChecksumBuilder( options, 0, 256 )
      
      self.building_nodes = self.finished_nodes = 0
      _buildChecksums( builder, src_files )
      self.assertEqual( self.building_nodes, 2 )
      self.assertEqual( self.building_nodes, self.finished_nodes )
      
      #//-------------------------------------------------------//
      
      self.building_nodes = self.finished_nodes = 0
      _buildChecksums( builder, src_files )
      self.assertEqual( self.building_nodes, 0 )
      self.assertEqual( self.building_nodes, self.finished_nodes )
      
      #//-------------------------------------------------------//
      
      builder = ChecksumBuilder( options, 32, 1024 )
      
      self.building_nodes = self.finished_nodes = 0
      _buildChecksums( builder, src_files )
      self.assertEqual( self.building_nodes, 2 )
      self.assertEqual( self.building_nodes, self.finished_nodes )
      
      #//-------------------------------------------------------//
      
      self.building_nodes = self.finished_nodes = 0
      _buildChecksums( builder, src_files )
      self.assertEqual( self.building_nodes, 0 )
      self.assertEqual( self.building_nodes, self.building_nodes )
  
  #//-------------------------------------------------------//
  
  def test_bm_nodes(self):
    
    def _makeNodes( builder ):
      node1 = Node( builder, value1 )
      copy_node1 = Node( builder, node1 )
      copy2_node1 = Node( builder, copy_node1 )
      node2 = Node( builder, value2 )
      node3 = Node( builder, value3 )
      copy_node3 = Node( builder, node3 )
      
      copy2_node3 = Node( builder, copy_node3 )
      copy2_node3.depends( [node1, copy_node1] )
      return node1, node2, node3, copy_node1, copy_node3, copy2_node1, copy2_node3
    
    with Tempdir() as tmp_dir:
      options = builtinOptions()
      options.build_dir = tmp_dir
    
      bm = BuildManager()
      
      value1 = SimpleValue( "http://aql.org/download1", name = "target_url1" )
      value2 = SimpleValue( "http://aql.org/download2", name = "target_url2" )
      value3 = SimpleValue( "http://aql.org/download3", name = "target_url3" )
      
      builder = CopyValueBuilder( options )
      
      bm.add( _makeNodes( builder ) )
      
      self.finished_nodes = 0
      bm.build( jobs = 1, keep_going = False )
      bm.close()
      self.assertEqual( self.finished_nodes, 7 )
      
      #// --------- //
      
      bm.add( _makeNodes( builder ) )
      
      self.actual_nodes = 0
      bm.status()
      bm.close()
      self.assertEqual( self.actual_nodes, 7 )
      
      #// --------- //
      
      bm.add( _makeNodes( builder ) )
      
      self.removed_nodes = 0
      bm.clear()
      bm.close()
      self.assertEqual( self.removed_nodes, 7 )
      
      #// --------- //
      
      bm.add( _makeNodes( builder ) )
      
      self.actual_nodes = 0
      self.outdated_nodes = 0
      bm.status()
      bm.close()
      self.assertEqual( self.actual_nodes, 0 )
      self.assertEqual( self.outdated_nodes, 3 )
      
      #// --------- //
      
      nodes = _makeNodes( builder )
      copy_node3 = nodes[4]
      bm.add( nodes )
      
      self.finished_nodes = 0
      bm.build( jobs = 1, keep_going = False, nodes = copy_node3 )
      bm.close()
      self.assertEqual( self.finished_nodes, 2 )
      
      #// --------- //
      
      nodes = _makeNodes( builder )
      node2 = nodes[1]; copy_node3  = nodes[4]
      bm.add( nodes )
      
      self.finished_nodes = 0
      bm.build( jobs = 1, keep_going = False, nodes = [node2, copy_node3] )
      bm.close()
      self.assertEqual( self.finished_nodes, 1 )
      
      #// --------- //
  
  #//-------------------------------------------------------//
  
  def test_bm_check(self):
    
    with Tempdir() as tmp_dir:
      options = builtinOptions()
      options.build_dir = tmp_dir
      
      src_files = self.generateSourceFiles( tmp_dir, 3, 201 )
      
      builder = ChecksumBuilder( options, 0, 256, replace_ext = True )
      
      self.building_nodes = self.finished_nodes = 0
      _buildChecksums( builder, src_files )
      self.assertEqual( self.building_nodes, 2 )
      self.assertEqual( self.building_nodes, self.finished_nodes )
      
      bm = _addNodesToBM( builder, src_files )
      try:
        self.actual_nodes = self.outdated_nodes = 0
        bm.status(); bm.selfTest()
        
        self.assertEqual( self.outdated_nodes, 0)
        self.assertEqual( self.actual_nodes, 2 )
        
      finally:
        bm.close()
  
  #//-------------------------------------------------------//
  
  def test_bm_batch(self):
    
    with Tempdir() as tmp_dir:
      options = builtinOptions()
      options.build_dir = tmp_dir
      
      src_files = self.generateSourceFiles( tmp_dir, 3, 201 )
      
      builder = ChecksumBuilder( options, 0, 256, replace_ext = True )
      
      self.building_nodes = self.finished_nodes = 0
      _buildChecksums( builder, src_files, Node = BatchNode )
      self.assertEqual( self.building_nodes, 2 )
      self.assertEqual( self.building_nodes, self.finished_nodes )
      
      bm = _addNodesToBM( builder, src_files, Node = BatchNode )
      try:
        self.actual_nodes = self.outdated_nodes = 0
        bm.status(); bm.selfTest()
        
        self.assertEqual( self.outdated_nodes, 0)
        self.assertEqual( self.actual_nodes, 2 )
        
      finally:
        bm.close()
  
  #//-------------------------------------------------------//
  
  def test_bm_rebuild(self):
    
    with Tempdir() as tmp_dir:
      options = builtinOptions()
      options.build_dir = tmp_dir
      
      num_src_files = 3
      src_files = self.generateSourceFiles( tmp_dir, num_src_files, 201 )
      
      bm = BuildManager()
      
      self.building_nodes = self.finished_nodes = 0
      self.actual_nodes = self.outdated_nodes = 0
      
      builder = ChecksumSingleBuilder( options, 0, 256 )
      
      src_values = []
      for s in src_files:
        src_values.append( FileChecksumValue( s ) )
      
      node = Node( builder, src_values )
      node = Node( builder, node )
      node = Node( builder, node )
      
      bm.add( node )
      _build( bm )
      
      self.assertEqual( self.building_nodes, num_src_files * 7 )
      
      #//-------------------------------------------------------//
      
      self.actual_nodes = self.outdated_nodes = 0
      
      bm = BuildManager()
      builder = ChecksumSingleBuilder( options, 0, 256 )
      
      node = Node( builder, src_values )
      bm.add( node ); bm.selfTest()
      bm.status(); bm.selfTest()
      
      self.assertEqual( self.outdated_nodes, 0 )
      self.assertEqual( self.actual_nodes, num_src_files )
  
  #//-------------------------------------------------------//
  
  def test_bm_tags(self):
    
    with Tempdir() as tmp_dir:
      options = builtinOptions()
      options.build_dir = tmp_dir
      
      num_src_files = 3
      src_files = self.generateSourceFiles( tmp_dir, num_src_files, 201 )
      
      builder = ChecksumSingleBuilder( options, 0, 256 )
      
      bm = BuildManager()
      
      self.finished_nodes = 0
      
      node = Node( builder, src_files )
      
      node_md5 = Node( builder, node.at('md5') )
      
      bm.add( node_md5 )
      
      _build( bm )
      
      self.assertEqual( self.finished_nodes, num_src_files * 2 )
      
      #//-------------------------------------------------------//
      
      self.touchCppFile( src_files[0] )
      
      bm = BuildManager()
      
      self.finished_nodes = 0
      
      node = Node( builder, src_files )
      
      node_md5 = Node( builder, node.at('md5') )
      
      bm.add( node_md5 )
      
      _build( bm )
      
      self.assertEqual( self.finished_nodes, 2 )
  
  #//-------------------------------------------------------//
  
  def test_bm_tags_batch(self):
    
    with Tempdir() as tmp_dir:
      options = builtinOptions()
      options.build_dir = tmp_dir
      
      num_src_files = 3
      src_files = self.generateSourceFiles( tmp_dir, num_src_files, 201 )
      
      builder = ChecksumBuilder( options, 0, 256 )
      single_builder = ChecksumSingleBuilder( options, 0, 256 )
      bm = BuildManager()
      
      self.finished_nodes = 0
      
      node = BatchNode( builder, src_files )
      
      node_md5 = Node( single_builder, node.at('md5') )
      
      bm.add( node_md5 )
      
      _build( bm )
      
      self.assertEqual( self.finished_nodes, num_src_files + 1 )
      
      #//-------------------------------------------------------//
      
      self.touchCppFile( src_files[0] )
      
      bm = BuildManager()
      
      self.finished_nodes = 0
      
      node = BatchNode( builder, src_files )
      
      node_md5 = Node( single_builder, node.at('md5') )
      
      bm.add( node_md5 )
      
      _build( bm )
      
      self.assertEqual( self.finished_nodes, 2 )

  #//-------------------------------------------------------//
  
  def test_bm_conflicts(self):
    
    with Tempdir() as tmp_dir:
      options = builtinOptions()
      options.build_dir = tmp_dir
      
      num_src_files = 3
      src_files = self.generateSourceFiles( tmp_dir, num_src_files, 201 )
      
      bm = BuildManager()
      
      self.finished_nodes = 0
      
      builder1 = ChecksumSingleBuilder( options, 0, 256 )
      builder2 = ChecksumSingleBuilder( options, 0, 1024 )
      
      node1 = Node( builder1, src_files )
      node2 = Node( builder2, src_files )
      # node1 = Node( builder1, node1 )
      # node2 = Node( builder2, node2 )
      
      bm.add( node1 )
      bm.add( node2 )
      self.assertRaises( ErrorNodeSignatureDifferent, _build, bm )
  
  #//-------------------------------------------------------//
  
  def test_bm_no_conflicts(self):
    
    with Tempdir() as tmp_dir:
      options = builtinOptions()
      options.build_dir = tmp_dir
      
      num_src_files = 3
      src_files = self.generateSourceFiles( tmp_dir, num_src_files, 201 )
      
      bm = BuildManager()
      
      self.finished_nodes = 0
      
      builder1 = ChecksumSingleBuilder( options, 0, 256 )
      builder2 = ChecksumSingleBuilder( options, 0, 256 )
      
      node1 = Node( builder1, src_files )
      node2 = Node( builder2, src_files )
      node1 = Node( builder1, node1 )
      node2 = Node( builder2, node2 )
      
      bm.add( node1 )
      bm.add( node2 )
      _build( bm )
      
      self.assertEqual( self.finished_nodes, 3 * 3 )
  
  #//-------------------------------------------------------//
  
  @skip
  def test_bm_node_names(self):
    
    with Tempdir() as tmp_dir:
      src_files = self.generateSourceFiles( tmp_dir, 3, 201 )
      options = builtinOptions()
      options.build_dir = tmp_dir
      
      builder = ChecksumBuilder( options, 0, 256, replace_ext = False )
      bm = BuildManager()
      try:
        src_values = []
        for s in src_files:
          src_values.append( FileChecksumValue( s ) )
        
        node0 = Node( builder, None )
        node1 = Node( builder, src_values )
        node2 = Node( builder, node1 )
        node3 = Node( builder, node2 )
        node4 = Node( builder, node3 )
        
        bm.add( node0 )
        bm.add( node1 )
        bm.add( node2 )
        bm.add( node3 )
        bm.add( node4 )
        
        bm.build(1, False)
        
        print("node2: %s" % str(node4) )
        print("node2: %s" % str(node3) )
        print("node2: %s" % str(node2) )
        print("node1: %s" % str(node1) )
        print("node0: %s" % str(node0) )
      
      finally:
        bm.close()

#//===========================================================================//

def   _generateNodeTree( bm, builder, node, depth ):
  while depth:
    node = Node( builder, node )
    bm.add( node )
    depth -= 1

#//===========================================================================//

@skip
class TestBuildManagerSpeed( AqlTestCase ):
  
  def test_bm_deps_speed(self):
    
    bm = BuildManager()
    
    value = SimpleValue( "http://aql.org/download", name = "target_url1" )
    builder = CopyValueBuilder()
    
    node = Node( builder, value )
    bm.add( node )
    
    _generateNodeTree( bm, builder, node, 5000 )

#//===========================================================================//

if __name__ == "__main__":
  runLocalTests()
