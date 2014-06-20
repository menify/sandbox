import sys
import os.path
import pickle

_search_paths = [ '.', 'tests_utils', 'tools' ]
sys.path[:0] = map( lambda p: os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..', p) ), _search_paths )

from tests_utils import TestCaseBase, skip, runTests, runLocalTests, TestsOptions
from aql.utils  import Tempfile
from aql.util_types import FilePaths

#//===========================================================================//

SRC_FILE_TEMPLATE = """
#include <cstdio>
#include "%s.h"

void  %s()
{}
"""

MAIN_SRC_FILE_TEMPLATE = """
#include <cstdio>

int  main()
{
  return 0;
}
"""

HDR_FILE_TEMPLATE = """
#ifndef HEADER_%s_INCLUDED
#define HEADER_%s_INCLUDED

extern void  %s();

#endif
"""

RES_FILE_TEMPLATE = """

#define VERSION_TEST "0.0.0.1"
#define VERSION_WORDS 0,0,0,1

VS_VERSION_INFO VERSIONINFO
FILEVERSION     VERSION_WORDS
PRODUCTVERSION  VERSION_WORDS
FILEFLAGSMASK   0x3fL
FILEFLAGS 0
BEGIN
  BLOCK "VarFileInfo"
  BEGIN
    VALUE "Translation",0x409,1200
  END
  BLOCK "StringFileInfo"
  BEGIN
    BLOCK "040904b0"
    BEGIN
      VALUE "CompanyName",  "Test\\0"
      VALUE "FileDescription",  "Test\\0"
      VALUE "FileVersion",  VERSION_TEST "\\0"
      VALUE "InternalName", "Test\\0"
      VALUE "LegalCopyright", "Copyright 2014 by Test\\0"
      VALUE "OriginalFilename", "Test\\0"
      VALUE "ProductName",  "Test\\0"
      VALUE "ProductVersion", VERSION_TEST "\\0"
    END
  END
END
"""

#//===========================================================================//

class AqlTestCase( TestCaseBase ):
  
  def _testSaveLoad( self, value ):
    data = pickle.dumps( ( value, ), protocol = pickle.HIGHEST_PROTOCOL )
    
    loaded_values = pickle.loads( data )
    loaded_value = loaded_values[0]
    
    self.assertEqual( value, loaded_value )
  
  #//===========================================================================//

  def   generateMainCppFile( self, dirname, name, content = None ):
    if not content:
      content = MAIN_SRC_FILE_TEMPLATE
    
    src_file = os.path.join( dirname, name + '.cpp' )
    
    with open( src_file, 'w' ) as f:
      f.write( content )
          
    return src_file

  #//===========================================================================//

  def   generateCppFile( self, dirname, name ):
    src_content = SRC_FILE_TEMPLATE % ( name, 'foo_' + name )
    hdr_content = HDR_FILE_TEMPLATE % ( name.upper(), name.upper(), 'foo_' + name )
    
    src_file = os.path.join( dirname, name + '.cpp' )
    hdr_file = os.path.join( dirname, name + '.h' )
    
    with open( src_file, 'w' ) as f:
      f.write( src_content )
    
    with open( hdr_file, 'w' ) as f:
      f.write( hdr_content )
    
    return src_file, hdr_file
  
  #//===========================================================================//
  
  def   generateResFile( self, dirname, name ):
    src_content = RES_FILE_TEMPLATE
    
    src_file = os.path.join( dirname, name + '.rc' )
    
    with open( src_file, 'w' ) as f:
      f.write( src_content )
    
    return src_file

  #//===========================================================================//

  def   generateCppFiles( self, dirname, name, count ):
    src_files = FilePaths()
    hdr_files = FilePaths()
    for i in range( count ):
      src_file, hdr_file = self.generateCppFile( dirname, name + str(i) )
      src_files.append( src_file )
      hdr_files.append( hdr_file )
    
    return src_files, hdr_files
  
  #//===========================================================================//
  
  @staticmethod
  def   generateFile( tmp_dir, start, stop ):
    tmp = Tempfile( dir = tmp_dir )
    tmp.write( bytearray( map( lambda v: v % 256, range( start, stop ) ) ) )
    
    tmp.close()
    
    return tmp
  
  #//===========================================================================//
  
  @staticmethod
  def   removeFiles( files ):
    for f in files:
      try:
        os.remove( f )
      except (OSError, IOError):
        pass
  
  #//===========================================================================//
  
  @staticmethod
  def   generateSourceFiles( tmp_dir, num, size ):
    
    src_files = []
    
    start = 0
    
    try:
      while num > 0:
        num -= 1
        src_files.append( AqlTestCase.generateFile( tmp_dir, start, start + size ) )
        start += size
    except:
      AqlTestCase.removeFiles( src_files )
      raise
    
    return src_files

#//===========================================================================//

if __name__ == '__main__':
  
  options = TestsOptions.instance()
  options.setDefault( 'test_modules_prefix', 'aql_test_' )
  
  runTests( options = options )
