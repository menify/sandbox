#
# Copyright (c) 2012 The developers of Aqualid project - http://aqualid.googlecode.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os.path

from aql_simple_types import FilePath

class BuildPathMapper( object ):
  
  __slots__ = (
    'build_dir',
    'build_dir_seq',
    'has_suffix',
  )
  
  def   __init__( self, build_dir_prefix, build_dir_name, build_dir_suffix ):
    
    build_dir = os.path.abspath( os.path.join( build_dir_prefix, build_dir_name, build_dir_suffix ) )
    
    self.build_dir      = build_dir
    self.build_dir_seq  = self.__seqPath( build_dir )
    self.has_suffix     = bool(build_dir_suffix)
  
  #//-------------------------------------------------------//
  
  @staticmethod
  def   __seqPath( path ):
    path = path.replace(':', os.path.sep)
    path = list( map( FilePath, filter( None, path.split( os.path.sep ) ) ) )
    
    return path
  
  #//-------------------------------------------------------//
  
  @staticmethod
  def __commonSeqPathSize( seq_path1, seq_path2 ):
    for i, parts in enumerate( zip( seq_path1, seq_path2 ) ):
      if parts[0] != parts[1]:
        return i
    
    return i + 1
  
  #//-------------------------------------------------------//
  
  def   getBuildPath( self, src_path = None ):
    if src_path is None:
      return self.build_dir
    
    if self.has_suffix:
      return os.path.join( self.build_dir, os.path.basename( src_path ) )
    
    src_path = os.path.abspath( src_path )
    src_path_seq = self.__seqPath( src_path )
    
    common_size = self.__commonSeqPathSize( self.build_dir_seq, src_path_seq )
    
    src_path_seq[ 0 : common_size ] = [ self.build_dir ]
    src_build_path = os.path.join( *src_path_seq )
    
    return src_build_path
  
  #//-------------------------------------------------------//
  def   getBuildPaths( self, src_paths ):
    
    paths = []
    for src_path in toSequence( src_paths ):
      paths.append( self.getBuildPath( src_path ) )
    
    return paths
  
  #//-------------------------------------------------------//
  
  def   getBuildFiles( self, src_files, exts, tmp_dir = None,
                        _splitext = os.path.splitext, _join = os.path.join, _basename = os.path.basename ):
    
    out_exts = tuple( toSequence( out_exts ) )
    
    out_files_lists = [ [] * len(out_exts) ]
    tmp_files_lists = [ [] * len(out_exts) ]
    
    for src_file in toSequence( src_files ):
      name = _splitext( src_file )[0]
      dst_file = self.getBuildPath( name )
      if tmp_dir:
        tmp_dst_file = _join( tmp_dir, _basename( src_file ) )
      
      for i, ext in enumerate( exts ):
        out_files_lists[i].append( dst_file + ext )
        if tmp_dir:
          tmp_files_lists[i].append( tmp_dst_file + ext )
    
    return out_files_lists + tmp_files_lists


#//===========================================================================//

def   getFilesFromValues( values ):
  
  files = []
  
  for value in values:
    if not isinstance( value, FileValue ):
      raise InvalidSourceValueType( value )
    
    files.append( value.name )
  
  return files

#//===========================================================================//

def   addPrefix( prefix, values ):
  return map( lambda v, prefix = prefix: prefix + v, values )

#//===========================================================================//

def   getOutputFiles( src_files, our_dir, out_exts,
                      _splitext = os.path.splitext, _join = os.path.join, _basename = os.path.basename ):
  
  out_exts = tuple( toSequence( out_exts ) )
  
  out_files_lists = [ [] * len(out_exts) ]
  
  for src_file in toSequence( src_files ):
    name = _splitext( _basename( src_file ) )[0]
    for i, ext in enumerate( out_exts ):
      out_files_lists[i].append( _join( out_dir, name ) + ext )
  
  return out_files_lists

#//===========================================================================//

def   moveFile( src_file, dst_file, _isdir = os.path.isdir, _makedirs = os.makedirs, _dirname = os.path.dirname ):
  dst_dir = _dirname( dst_file )
  if not _isdir( dst_dir ):
    _makedirs( dst_dir )
  shutil.move( src_file, dst_file )

#//===========================================================================//

def   _moveTempFiles( src_files, *tmp_dst_files)
  for src_file, obj_file in zip( src_files, obj_files ):
      if os.path.isfile( obj_file ):
        target_obj_file = outdir_mapper.getBuildPath( src_file )
        moveFile( target_obj_file, src_file )

