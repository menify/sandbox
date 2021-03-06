import os
import re
import itertools

import aql

from cpp_common import  ToolCommonCpp, CommonCppCompiler, CommonCppArchiver, CommonCppLinker,\
                        ToolCommonRes, CommonResCompiler

#//===========================================================================//
#// BUILDERS IMPLEMENTATION
#//===========================================================================//

def   _readDeps( dep_file, exclude_dirs, _space_splitter_re = re.compile(r'(?<!\\)\s+') ):
  
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
    
    dep_files += map( os.path.abspath, tmp_dep_files )
  
  dep_files = iter(dep_files)
  next( dep_files ) # skip the source file
  
  dep_files = tuple( dep_file for dep_file in dep_files if not dep_file.startswith( exclude_dirs ) )
  
  return dep_files

#//===========================================================================//

#noinspection PyAttributeOutsideInit
class GccCompiler (CommonCppCompiler):
  
  def   build( self, node ):
    
    sources = node.getSources()
    
    obj_file = self.getObjPath( sources[0] )
    cwd = obj_file.dirname()
    
    with aql.Tempfile( prefix = obj_file, suffix = '.d', dir = cwd ) as dep_file:
      
      cmd = list(self.cmd)
      
      cmd += ['-c', '-o', obj_file, '-MMD', '-MF', dep_file]
      cmd += sources
      
      out = self.execCmd( cmd, cwd, file_flag = '@' )
      
      node.addTargets( obj_file, implicit_deps = _readDeps( dep_file, self.ext_cpppath ) )
      
      return out

#//===========================================================================//

class GccResCompiler (CommonResCompiler):
  
  def   build( self, node ):
    
    src = node.getSources()[0]
    
    res_file = self.getObjPath( src )
    cwd = res_file.dirname()
    
    cmd = list(self.cmd)
    cmd += [ '-o', res_file, '-i', src ]
    
    out = self.execCmd( cmd, cwd, file_flag = '@' )
    
    # deps = _parseRes( src )
    
    node.addTargets( res_file )
    
    return out

#//===========================================================================//

class GccCompilerMaker (object):
  def   makeCompiler( self, options ):
    return GccCompiler( options )
  
  def   makeResCompiler( self, options ):
    return GccResCompiler( options )

#//===========================================================================//

class GccArchiver (GccCompilerMaker, CommonCppArchiver ):
  
  def   build( self, node ):
    
    cmd = list(self.cmd)
    cmd.append( self.target )
    cmd += node.getSources()
    
    cwd = self.target.dirname()
    
    out = self.execCmd( cmd, cwd = cwd, file_flag = '@' )
    
    node.addTargets( self.target )
    
    return out

#//===========================================================================//

class GccLinker( GccCompilerMaker, CommonCppLinker ):
  
  def   build( self, node ):
    
    cmd = list(self.cmd)
    
    obj_files = node.getSources()
    
    cmd[2:2] = obj_files
    
    if self.shared:
      cmd += [ '-shared' ]
      tags = ('shlib','implib')
    else:
      tags = None
          
    cmd += [ '-o', self.target ]
    
    cwd = self.target.dirname()
    
    out = self.execCmd( cmd, cwd = cwd, file_flag = '@' )
    
    node.addTargets( self.target, tags = tags )
    
    return out

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
  
  out = result.output
  
  match = target_re.search( out )
  target = match.group(1).strip() if match else ''
  
  match = version_re.search( out )
  version = str(aql.Version( match.group(1).strip() if match else '' ))
  
  target_list = target.split('-', 2)
  
  target_os = target_list[-1]
  if len(target_list) > 1:
    target_arch = target_list[0]
  else:
    target_arch = 'native'
  
  if target_os.find('mingw32') != -1:
    target_os = 'windows'
  
  specs = {
    'cc_name':      'gcc',
    'cc_ver':       version,
    'target_os':    target_os,
    'target_arch':  target_arch,
  }
  
  return specs

#//===========================================================================//

class ToolGccCommon( ToolCommonCpp ):
  
  @classmethod
  def   setup( cls, options, env ):
    
    gcc_prefix = options.gcc_prefix.get()
    gcc_suffix = options.gcc_suffix.get()
    
    gcc, gxx, ar = _findGcc( env, gcc_prefix, gcc_suffix )
    specs = _getGccSpecs( gcc )
    
    options.update( specs )
    
    if cls.language == 'c':
      options.cc = gcc
      options.link = gcc
    else:
      options.cc = gxx
      options.link = gxx
    
    options.lib = ar
    
    options.rc = aql.findOptionalProgram( 'windres', env )
  
  #//-------------------------------------------------------//
  
  @classmethod
  def   options( cls ):
    options = super(ToolGccCommon, cls).options()
    
    options.gcc_path    = aql.PathOptionType()
    options.gcc_target  = aql.StrOptionType( ignore_case = True )
    options.gcc_prefix  = aql.StrOptionType( description = "GCC C/C++ compiler prefix" )
    options.gcc_suffix  = aql.StrOptionType( description = "GCC C/C++ compiler suffix" )
    
    return options
  
  #//-------------------------------------------------------//
  
  def   __init__(self, options ):
    super(ToolGccCommon,self).__init__( options )
    
    options.env['CPATH']  = aql.ListOptionType( value_type = aql.PathOptionType(), separators = os.pathsep )
    if self.language == 'c':
      options.env['C_INCLUDE_PATH'] = aql.ListOptionType( value_type = aql.PathOptionType(), separators = os.pathsep )
    else:
      options.env['CPLUS_INCLUDE_PATH'] = aql.ListOptionType( value_type = aql.PathOptionType(), separators = os.pathsep )
    
    options.env['LIBRARY_PATH'] = aql.ListOptionType( value_type = aql.PathOptionType(), separators = os.pathsep )
    
    if_ = options.If()
    if_windows = if_.target_os.eq('windows')
    
    options.objsuffix     = '.o'
    options.ressuffix     = options.objsuffix
    options.libprefix     = 'lib'
    options.libsuffix     = '.a'
    options.shlibprefix   = 'lib'
    options.shlibsuffix   = '.so'
    if_windows.shlibprefix = ''
    if_windows.shlibsuffix = '.dll'
    if_windows.progsuffix = '.exe'
    
    options.cpppath_prefix    = '-I '
    options.libpath_prefix    = '-L '
    options.cppdefines_prefix = '-D '
    options.libs_prefix = '-l'
    options.libs_suffix = ''

    options.ccflags   += ['-pipe', '-x', self.language ]
    options.libflags  += ['-rcs']
    options.linkflags += ['-pipe']
    
    options.language = self.language
    
    if_.rtti.isTrue().cxxflags   += '-frtti'
    if_.rtti.isFalse().cxxflags  += '-fno-rtti'
    
    if_.exceptions.isTrue().cxxflags   += '-fexceptions'
    if_.exceptions.isFalse().cxxflags  += '-fno-exceptions'
    
    if_windows.target_subsystem.eq('console').linkflags += '-Wl,--subsystem,console'
    if_windows.target_subsystem.eq('windows').linkflags += '-Wl,--subsystem,windows'
    
    if_.debug_symbols.isTrue().ccflags += '-g'
    if_.debug_symbols.isFalse().linkflags += '-Wl,--strip-all'
    
    if_.runtime_link.eq('static').linkflags += '-static-libgcc'
    if_.runtime_link.eq('shared').linkflags += '-shared-libgcc'
    
    if_.target_os.eq('windows').runtime_thread.eq('multi').ccflags += '-mthreads'
    if_.target_os.ne('windows').runtime_thread.eq('multi').ccflags += '-pthreads'
    
    if_.optimization.eq('speed').occflags += '-Ofast'
    if_.optimization.eq('size').occflags  += '-Os'
    if_.optimization.eq('off').occflags   += '-O0'
    
    if_.inlining.eq('off').occflags   += '-fno-inline'
    if_.inlining.eq('on').occflags    += '-finline'
    if_.inlining.eq('full').occflags  += '-finline-functions'
    
    if_.warning_as_error.isTrue().ccflags += '-Werror'
    
    if_profiling_true = if_.profile.isTrue()
    if_profiling_true.ccflags += '-pg'
    if_profiling_true.linkflags += '-pg'
    
    if_cxxstd = if_.cxxstd
    
    if_cxx11 = if_cxxstd.eq('c++11')
    if_cxx14 = if_cxxstd.eq('c++14')
    
    if_cxxstd.eq('c++98').cxxflags  += '-std=c++98'
    if_cxx11.cc_ver.ge("4.7").cxxflags += '-std=c++11'
    if_cxx11.cc_ver.ge("4.3").cc_ver.le("4.6").cxxflags += '-std=c++0x'
    if_cxx14.cc_ver.ge("4.8").cxxflags += '-std=c++1y'
    
    if_.pic.isTrue().target_os.notIn(['windows', 'cygwin'] ).ccflags += '-fPIC'
  
  #//-------------------------------------------------------//
  
  def   Compile( self, options ):
    return GccCompiler( options )
  
  def   CompileResource( self, options ):
    return GccResCompiler( options )
  
  def   LinkStaticLibrary( self, options, target ):
    return GccArchiver( options, target )
  
  def   LinkSharedLibrary( self, options, target ):
    return GccLinker( options, target, shared = True )
  
  def   LinkProgram( self, options, target ):
    return GccLinker( options, target, shared = False )

#//===========================================================================//

@aql.tool('c++', 'g++', 'cpp', 'cxx')
class ToolGxx( ToolGccCommon ):
  language = "c++"

#//===========================================================================//

@aql.tool('c', 'gcc', 'cc')
class ToolGcc( ToolGccCommon ):
  language = "c"

#//===========================================================================//

@aql.tool('rc', 'msrc')
class ToolWindRes( ToolCommonRes ):
  
  @classmethod
  def   setup( cls, options, env ):
    
    rc = aql.whereProgram( 'windres', env )
    options.target_os = 'windows'
    options.rc = rc
  
  def   __init__(self, options ):
    super(ToolWindRes,self).__init__( options )
    options.ressuffix = '.o'
      
  def   Compile( self, options ):
    return GccResCompiler( options )
