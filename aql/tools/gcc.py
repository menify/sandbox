import os
import re
import itertools

import aql

#//===========================================================================//
#// BUILDERS IMPLEMENTATION
#//===========================================================================//

def   _isCCppSourceFile( source_file ):
  ext = os.path.splitext( str(source_file) )[1]
  return ext in ( ".cc", ".cp", ".cxx", ".cpp", ".CPP", ".c++", ".C", ".c" )

#//===========================================================================//

def   _readDeps( dep_file, _space_splitter_re = re.compile(r'(?<!\\)\s+') ):
  
  deps = aql.readTextFile( dep_file )
  
  dep_files = []
  
  target_sep = ': '
  target_sep_len = len(target_sep)
  
  for line in deps.splitlines():
    pos = line.find( target_sep )
    if pos >= 0:
      line = line[ pos + target_sep_len: ]
    
    line = line.rstrip('\\ ').strip()
    
    tmp_dep_files = filter( None, _space_splitter_re.split( line ) )
    tmp_dep_files = [dep_file.replace('\\ ', ' ') for dep_file in tmp_dep_files ]
    
    dep_files += tmp_dep_files
  
  return dep_files[1:]  # skip the source file

#//===========================================================================//

def   _addPrefix( prefix, values ):
  return map( lambda v, prefix = prefix: prefix + v, values )

#//===========================================================================//

#noinspection PyAttributeOutsideInit
class GccCompiler (aql.FileBuilder):
  
  NAME_ATTRS = ( 'prefix', 'suffix' )
  SIGNATURE_ATTRS = ('cmd', )
  
  #//-------------------------------------------------------//
  
  #noinspection PyUnusedLocal
  def   __init__(self, options, language, shared ):
    
    self.prefix = options.prefix.get()
    self.suffix = options.shobjsuffix.get() if shared else options.objsuffix.get()
    
    self.cmd = self.__getCmd( options, language, shared )
  
  #//-------------------------------------------------------//
  
  @staticmethod
  def   __getCmd( options, language, shared ):
    
    if language == 'c++':
      cmd = [ str(options.cxx.get()) ]
    else:
      cmd = [ str(options.cc.get()) ]
    
    cmd += ['-c', '-pipe', '-MMD', '-x', language ]
    if language == 'c++':
      cmd += options.cxxflags.get()
    else:
      cmd += options.cflags.get()
    
    if shared:
      cmd += ['-fPIC']
    
    cmd += options.ccflags.get()
    cmd += itertools.chain( *itertools.product( ['-D'], options.cppdefines.get() ) )
    cmd += itertools.chain( *itertools.product( ['-I'], options.cpppath.get() ) )
    cmd += itertools.chain( *itertools.product( ['-I'], options.ext_cpppath.get() ) )
    
    return cmd
  
  #//-------------------------------------------------------//
  
  def   getTargetValues( self, node ):
    
    obj_file = self._getObj( node )[0]
    
    value_type = self.fileValueType()
    target = value_type( name = obj_file, signature = None )
    
    return target
  
  #//-------------------------------------------------------//
  
  def   _getObj(self, node ):
    source = node.getSources()[0]
    obj_file = self.getBuildPath( source )
    obj_file = obj_file.change( prefix = self.prefix ) + self.suffix
    
    return obj_file, source

  #//-------------------------------------------------------//
  
  def   build( self, node ):
    
    obj_file, source = self._getObj( node )
    cwd = obj_file.dirname()
    
    with aql.Tempfile( prefix = obj_file, suffix = '.d', dir = cwd ) as dep_file:
      
      cmd = list(self.cmd)
      cmd += ['-o', obj_file, '-MF', dep_file, source ]
      
      out = self.execCmd( cmd, cwd, file_flag = '@' )
      
      node.setFileTargets( obj_file, ideps = _readDeps( dep_file ) )
      
      return out
  
  #//-------------------------------------------------------//
  
  def   getTraceName( self, brief ):
    if brief:
      name = self.cmd[0]
      name = os.path.splitext( os.path.basename( name ) )[0]
    else:
      name = ' '.join( self.cmd )
    
    return name
  
#//===========================================================================//

#noinspection PyAttributeOutsideInit
class GccLinkerBase(aql.FileBuilder):
  
  NAME_ATTRS = ('target', )
  SIGNATURE_ATTRS = ('cmd', )

  #//-------------------------------------------------------//
  
  def   prebuild( self, node ):
    obj_files = []
    
    compiler = GccCompiler( node.options, self.language, shared = False )
    src_nodes = []
    for src_file in node.getSourceValues():
      if _isCCppSourceFile( src_file.name ):
        src_node = aql.Node( compiler, src_file, node.cwd )
        src_nodes.append( src_node )
      else:
        obj_files.append( src_file )
    
    node.builder_data = obj_files
    
    return src_nodes
  
  #//-------------------------------------------------------//
  
  def   prebuildFinished( self, node, pre_nodes ):
    
    obj_files = node.builder_data
    for pre_node in pre_nodes:
      obj_files.extend( pre_node.getTargets() )
    
    return False
  
  #//-------------------------------------------------------//
  
  def   getTargetValues( self, node ):
    value_type = self.fileValueType()
    target = value_type( name = self.target, signature = None )
    return target
  
  #//-------------------------------------------------------//
  
  def   getTraceSources( self, node, brief ):
    return node.builder_data
  
  #//-------------------------------------------------------//
  
  def   getTraceName( self, brief ):
    if brief:
      name = self.cmd[0]
      name = os.path.splitext( os.path.basename( name ) )[0]
    else:
      name = ' '.join( self.cmd )
    
    return name

#//===========================================================================//

#noinspection PyAttributeOutsideInit
class GccArchiver(GccLinkerBase):
  
  def   __init__( self, options, target, language ):
    
    prefix = options.libprefix.get() + options.prefix.get()
    suffix = options.libsuffix.get()
    
    self.target = self.getBuildPath( target ).change( prefix = prefix ) + suffix
    self.language = language

    self.cmd = [ options.lib.get(), 'rcs' ]
    
  #//-------------------------------------------------------//
  
  def   build( self, node ):
    
    obj_files = tuple( src.get() for src in node.builder_data )
    
    cmd = list(self.cmd)
    cmd.append( self.target )
    cmd += obj_files
    
    cwd = self.target.dirname()
    
    out = self.execCmd( cmd, cwd = cwd, file_flag = '@' )
    
    node.setFileTargets( self.target )
    
    return out

#//===========================================================================//

#noinspection PyAttributeOutsideInit
class GccLinker(GccLinkerBase):
  
  def   __init__( self, options, target, language, shared ):
    if shared:
      prefix = options.shlibprefix.get() + options.prefix.get()
      suffix = options.shlibsuffix.get()
    else:
      prefix = options.prefix.get()
      suffix = options.progsuffix.get()
    
    self.target = self.getBuildPath( target ).change( prefix = prefix, ext = suffix )
    
    self.cmd = self.__getCmd( options, self.target, language, shared )
    self.language = language
    
  #//-------------------------------------------------------//
  
  @staticmethod
  def   __getCmd( options, target, language, shared ):
    
    if language == 'c++':
      cmd = [ options.cxx.get() ]
    else:
      cmd = [ options.cc.get() ]
    
    cmd += [ '-pipe' ]
    
    if shared:
      cmd += [ '-shared' ]
    
    cmd += options.linkflags.get()
    cmd += itertools.chain( *itertools.product( ['-L'], options.libpath.get() ) )
    cmd += itertools.chain( *itertools.product( ['-l'], options.libs.get() ) )
    
    return cmd
  
  #//-------------------------------------------------------//
  
  def   build( self, node ):
    
    obj_files = tuple( src.get() for src in node.builder_data )
    
    cmd = list(self.cmd)
    
    cmd[2:2] = obj_files
    
    cmd += [ '-o', str(self.target) ]
    
    cwd = self.target.dirname()
    
    out = self.execCmd( cmd, cwd = cwd, file_flag = '@' )
    
    node.setFileTargets( self.target )
    
    return out
  
  #//-------------------------------------------------------//
  
  def   getTargetValues( self, node ):
    value_type = self.fileValueType()
    target = value_type( name = self.target, signature = None )
    return target
  
  #//-------------------------------------------------------//

#//===========================================================================//
#// TOOL IMPLEMENTATION
#//===========================================================================//

def   _checkProg( gcc_path, prog ):
  prog = os.path.join( gcc_path, prog )
  return prog if os.path.isfile( prog ) else None

#//===========================================================================//

def   _findGcc( env, gcc_prefix, gcc_suffix ):
  gcc = '%sgcc%s' % (gcc_prefix, gcc_suffix)
  gcc = aql.whereProgram( gcc, env )
  
  gxx = None
  ar = None
  
  gcc_ext = os.path.splitext( gcc )[1]
  
  gcc_prefixes = [gcc_prefix, ''] if gcc_prefix else ['']
  gcc_suffixes = [gcc_suffix + gcc_ext, gcc_ext ] if gcc_suffix else [gcc_ext]
  
  gcc_path = os.path.dirname( gcc )
  
  for gcc_prefix, gcc_suffix in itertools.product( gcc_prefixes, gcc_suffixes ):
    if not gxx: gxx = _checkProg( gcc_path, '%sg++%s' % (gcc_prefix, gcc_suffix) )
    if not gxx: gxx = _checkProg( gcc_path, '%sc++%s' % (gcc_prefix, gcc_suffix) )
    if not ar:  ar  = _checkProg( gcc_path, '%sar%s' % (gcc_prefix, gcc_suffix) )
  
  if not gxx or not ar:
    raise NotImplementedError()
  
  return gcc, gxx, ar

#//===========================================================================//

def   _getGccSpecs( gcc ):
  result = aql.executeCommand( [gcc, '-v'] )
  
  target_re = re.compile( r'^\s*Target:\s+(.+)$', re.MULTILINE )
  version_re = re.compile( r'^\s*gcc version\s+(.+)$', re.MULTILINE )
  
  out = result.out
  
  match = target_re.search( out )
  target = match.group(1).strip() if match else ''
  
  match = version_re.search( out )
  version = str(aql.Version( match.group(1).strip() if match else '' ))
  
  if target == 'mingw32':
    target_arch = 'x86-32'
    target_os = 'windows'
  
  else:
    target_list = target.split('-')
    
    target_list_len = len( target_list )
    
    if target_list_len == 2:
      target_arch = target_list[0]
      target_os = target_list[1]
    elif target_list_len > 2:
      target_arch = target_list[0]
      target_os = target_list[2]
    else:
      target_arch = ''
      target_os = ''
  
  specs = {
    'cc_name':      'gcc',
    'cc_ver':       version,
    'target_os':    target_os,
    'target_arch':  target_arch,
  }
  
  return specs

#//===========================================================================//

class ToolGccCommon( aql.Tool ):
  
  @staticmethod
  def   setup( options, env ):
    
    gcc_prefix = options.gcc_prefix.get()
    gcc_suffix = options.gcc_suffix.get()
    
    """
    cfg_keys = ( gcc_prefix, gcc_suffix )
    cfg_deps = ( str(options.env['PATH']), )
    
    specs = self.LoadValues( project, cfg_keys, cfg_deps )
    if cfg is None:
      info = _getGccInfo( env, gcc_prefix, gcc_suffix )
      self.SaveValues( project, cfg_keys, cfg_deps, specs )
    """
    
    gcc, gxx, ar = _findGcc( env, gcc_prefix, gcc_suffix )
    specs = _getGccSpecs( gcc )
    
    options.update( specs )
    
    options.cc = gcc
    options.cxx = gxx
    options.lib = ar
  
  #//-------------------------------------------------------//
  
  @staticmethod
  def   options():
    
    options = aql.optionsCCpp()
    
    options.gcc_path  = aql.PathOptionType()
    options.gcc_target = aql.StrOptionType( ignore_case = True )
    options.gcc_prefix = aql.StrOptionType( description = "GCC C/C++ compiler prefix" )
    options.gcc_suffix = aql.StrOptionType( description = "GCC C/C++ compiler suffix" )
    
    if_ = options.If()
    if_windows = if_.target_os.eq('windows')
    
    options.objsuffix     = '.o'
    options.shobjsuffix   = '.os'
    options.libprefix     = 'lib'
    options.libsuffix     = '.a'
    options.shlibprefix   = 'lib'
    options.shlibsuffix   = '.so'
    if_windows.progsuffix = '.exe'
    
    if_windows.target_subsystem.eq('console').linkflags += '-Wl,--subsystem,console'
    if_windows.target_subsystem.eq('windows').linkflags += '-Wl,--subsystem,windows'
    
    if_.debug_symbols.isTrue().ccflags += '-g'
    if_.debug_symbols.isFalse().linkflags += '-Wl,--strip-all'
    
    if_.runtime_link.eq('static').linkflags += '-static-libgcc'
    if_.runtime_link.eq('shared').linkflags += '-shared-libgcc'
    
    if_.target_os.eq('windows').runtime_thread.eq('multi').ccflags += '-mthreads'
    if_.target_os.ne('windows').runtime_thread.eq('multi').ccflags += '-pthreads'
    
    if_.optimization.eq('speed').occflags += '-O3'
    if_.optimization.eq('size').occflags  += '-Os'
    if_.optimization.eq('off').occflags   += '-O0'
    
    if_.inlining.eq('off').occflags   += '-fno-inline'
    if_.inlining.eq('on').occflags    += '-finline'
    if_.inlining.eq('full').occflags  += '-finline-functions'
    
    if_.no_rtti.isTrue().cxxflags   += '-fno-rtti'
    if_.no_rtti.isFalse().cxxflags  += '-frtti'
    
    if_.no_exceptions.isTrue().cxxflags   += '-fno-exceptions'
    if_.no_exceptions.isFalse().cxxflags  += '-fexceptions'
    
    if_.warning_as_error.isTrue().ccflags += '-Werror'
    
    if_profiling_true = if_.profile.isTrue()
    if_profiling_true.ccflags += '-pg'
    if_profiling_true.linkflags += '-pg'
    #~ if_profiling_true.linkflags -= '-Wl,--strip-all'
    
    options.setGroup( "C/C++ compiler" )
    
    return options
  
  #//-------------------------------------------------------//
  
  def   Compile( self, options, shared = False, batch = False ):
    builder = GccCompiler( options, self.language, shared = shared )
    if batch:
      return aql.BuildBatch( builder )
    return aql.BuildSingle( builder )
  
  def   LinkLibrary( self, options, target ):
    return GccArchiver( options, target, self.language )
  
  def   LinkSharedLibrary( self, options, target ):
    return GccLinker( options, target, self.language, shared = True )
  
  def   LinkProgram( self, options, target ):
    return GccLinker( options, target, self.language, shared = False )

#//===========================================================================//

@aql.tool('c++', 'g++', 'cpp', 'cxx')
class ToolGxx( ToolGccCommon ):
  language = "c++"

#//===========================================================================//

@aql.tool('c', 'gcc', 'cc')
class ToolGcc( ToolGccCommon ):
  language = "c"
