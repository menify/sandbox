#
# Copyright (c) 2012-2014 The developers of Aqualid project - http://aqualid.googlecode.com
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

__all__ = ( 'Project', 'ProjectConfig',
            'ErrorProjectBuilderMethodFewArguments',
            'ErrorProjectBuilderMethodUnbound',
            'ErrorProjectBuilderMethodWithKW',
            'ErrorProjectInvalidMethod',
          )

import os.path
import types
import itertools

from aql.utils import CLIConfig, CLIOption, getFunctionArgs, execFile, flattenList, findFiles, cpuCount, Chdir
from aql.util_types import FilePath, FilePaths, SplitListType, toSequence, AqlException
from aql.values import NullValue, ValueBase, FileTimestampValue, FileChecksumValue, DirValue
from aql.options import builtinOptions, Options
from aql.nodes import BuildManager, Node, BatchNode, BuildBatch

from .aql_tools import ToolsManager
from .aql_builtin_tools import BuiltinTool

#//===========================================================================//

class   ErrorProjectInvalidMethod( AqlException ):
  def   __init__( self, method ):
    msg = "Invalid project method: '%s'" % (method,)
    super(type(self), self).__init__( msg )

#//===========================================================================//

class   ErrorProjectUnknownTarget( AqlException ):
  def   __init__( self, target ):
    msg = "Unknown build target: '%s'" % (target,)
    super(type(self), self).__init__( msg )

#//===========================================================================//

class   ErrorProjectBuilderMethodWithKW( AqlException ):
  def   __init__( self, method ):
    msg = "Keyword arguments are not allowed in builder method: '%s'" % (method,)
    super(type(self), self).__init__( msg )

#//===========================================================================//

class   ErrorProjectBuilderMethodUnbound( AqlException ):
  def   __init__( self, method ):
    msg = "Unbound builder method: '%s'" % (method,)
    super(type(self), self).__init__( msg )

#//===========================================================================//

class   ErrorProjectBuilderMethodFewArguments( AqlException ):
  def   __init__( self, method ):
    msg = "Too few arguments in builder method: '%s'" % (method,)
    super(type(self), self).__init__( msg )

#//===========================================================================//

class   ErrorProjectBuilderMethodInvalidOptions( AqlException ):
  def   __init__( self, value ):
    msg = "Type of 'options' argument must be Options, instead of : '%s'(%s)" % (type(value), value)
    super(type(self), self).__init__( msg )

#//===========================================================================//

#noinspection PyUnresolvedReferences
class ProjectConfig( object ):
  
  __slots__ = ('directory', 'makefile', 'targets', 'options',
               'verbose', 'log_level', 'jobs', 'keep_going',
               'build_always', 'profile', 'memory', 'clean', 'status' )
  
  #//-------------------------------------------------------//
  
  def   __init__( self, args = None ):
    
    CLI_USAGE = "usage: %prog [FLAGS] [[TARGET] [OPTION=VALUE] ...]"
    
    Paths = SplitListType( FilePaths, ', ' )
    
    CLI_OPTIONS = (
      
      CLIOption( "-C", "--directory",       "directory",      FilePath,   '',           "Change directory before reading the make files.", 'FILE PATH'),
      CLIOption( "-f", "--makefile",        "makefile",       FilePath,   'make.aql',   "Path to a make file.", 'FILE PATH'),
      CLIOption( "-l", "--list-options",    "list_options",   bool,       False,        "List all available options and exit." ),
      CLIOption( "-c", "--config",          "config",         FilePath,   None,         "The configuration file used to read CLI arguments." ),
      CLIOption( "-B", "--always",          "build_always",   bool,       False,        "Unconditionally build all targets." ),
      CLIOption( "-R", "--clean",           "clean",          bool,       False,        "Cleans targets." ),
      CLIOption( "-n", "--status",          "status",         bool,       False,        "Print status of targets." ),
      CLIOption( "-u", "--up",              "search_up",      bool,       False,        "Search up directory tree for a make file." ),
      
      CLIOption( "-b", "--build-directory", "build_dir",      FilePath,   'output',     "Build output path.", 'FILE PATH'),
      CLIOption( "-I", "--tools-path",      "tools_path",     Paths,      [],           "Path to tools and setup scripts.", 'FILE PATH, ...'),
      CLIOption( "-k", "--keep-going",      "keep_going",     bool,       False,        "Keep going when some targets can't be built." ),
      CLIOption( "-j", "--jobs",            "jobs",           int,        None,         "Number of parallel jobs to process targets.", 'NUMBER' ),
      CLIOption( "-v", "--verbose",         "verbose",        bool,       False,        "Verbose mode." ),
      CLIOption( "-s", "--silent",          "silent",         bool,       False,        "Silent mode." ),
      CLIOption( "-d", "--debug",           "debug",          bool,       False,        "Debug logs." ),
      CLIOption( "-m", "--memory",          "memory",         bool,       False,        "Display memory usage." ),
      CLIOption( "-p", "--profile",         "profile",        FilePath,   None,         "Run under profiler and save the results in the specified file." ),
    )
    
    cli_config = CLIConfig( CLI_USAGE, CLI_OPTIONS, args )
    
    options = builtinOptions()
    
    config = cli_config.config
    
    if config:
      cli_config.readConfig( config, { 'options': options })
    
    cli_options = {}
    
    ignore_options = {'list_options', 'config'}
    ignore_options.update( ProjectConfig.__slots__ )
    
    for name,value in cli_config.items():
      if (name not in ignore_options) and (value is not None):
        cli_options[ name ] = value
    
    options.update( cli_options )
    
    if cli_config.list_options:
      printOptions( options )
    
    #//-------------------------------------------------------//
    
    log_level = 1
    if cli_config.debug:
      log_level = 2
    if cli_config.silent:
      log_level = 0
    
    #//-------------------------------------------------------//
    
    self.options      = options
    self.directory    = cli_config.directory.abspath()
    self.makefile     = cli_config.makefile
    self.targets      = cli_config.targets
    self.verbose      = cli_config.verbose
    self.keep_going   = cli_config.keep_going
    self.build_always = cli_config.build_always
    self.clean        = cli_config.clean
    self.status       = cli_config.status
    self.jobs         = cli_config.jobs
    self.profile      = cli_config.profile
    self.memory       = cli_config.memory
    self.log_level    = log_level

#//===========================================================================//

class BuilderWrapper( object ):
  __slots__ = ( 'project', 'options', 'method', 'arg_names' )
  
  def   __init__( self, method, project, options ):
    self.arg_names  = self.__checkBuilderMethod( method )
    self.method     = method
    self.project    = project
    self.options    = options

  #//-------------------------------------------------------//
  
  @staticmethod
  def   __checkBuilderMethod( method ):
    if not hasattr(method, '__call__'):
      raise ErrorProjectInvalidMethod( method )
    
    f_args, f_varargs, f_kw, f_defaults = getFunctionArgs( method )
    
    if f_kw:
      raise ErrorProjectBuilderMethodWithKW( method )
    
    min_args = 1  # at least one argument: options
    
    if isinstance( method, types.MethodType ):
      if method.__self__ is None:
        raise ErrorProjectBuilderMethodUnbound( method )
      
    if len(f_args) < min_args:
      raise ErrorProjectBuilderMethodFewArguments( method )
    
    return frozenset( f_args )
  
  #//-------------------------------------------------------//
  
  def   __getOptionsAndArgs( self, kw ):
    args_kw = {}
    sources = []
    deps = []
    
    options = kw.pop("options", None )
    if options is not None:
      if not isinstance( options, Options ):
        raise ErrorProjectBuilderMethodInvalidOptions( options )
    else:
      options = self.options
    
    options = options.override()
    
    for name, value in kw.items():
      if name in ['sources', 'source']:
        sources += toSequence( value )
      else:
        for v in toSequence( value ):
          if isinstance( v, (Node, ValueBase) ):
            deps.append( v )
        
        if name in self.arg_names:
          args_kw[ name ] = value
        else:
          options[ name ] = value
    
    return options, deps, sources, args_kw
  
  #//-------------------------------------------------------//
  
  def   __call__( self, *args, **kw ):
    
    options, deps, sources, args_kw = self.__getOptionsAndArgs( kw )
    
    sources += args
    sources = flattenList( sources )
    
    builder = self.method( options, **args_kw )
    
    if isinstance( builder, BuildBatch ):
      node = BatchNode( builder, sources )
    else:
      node = Node( builder, sources )

    node.depends( deps )

    self.project.AddNodes( node )
    
    return node

#//===========================================================================//

class ToolWrapper( object ):
  
  def   __init__( self, tool, project, options ):
    self.project = project
    self.options = options
    self.tool = tool
  
  #//-------------------------------------------------------//
  
  def   __getattr__( self, attr ):
    method = getattr( self.tool, attr )
    
    if attr.startswith('_') or not isinstance( method, types.MethodType ):
      return method
    
    builder = BuilderWrapper( method, self.project, self.options )
    
    setattr( self, attr, builder )
    return builder

#//===========================================================================//

class ProjectTools( object ):
  
  def   __init__( self, project ):
    self.project = project
    self.tools_cache = {}
    
    tools = ToolsManager.instance()
    tools.loadTools( self.project.options.tools_path.get() )
    
    self.tools = tools
  
  #//-------------------------------------------------------//
  
  def   _override( self, project ):
    other = super(ProjectTools,self).__new__( self.__class__ )
    
    other.project = project
    other.tools = self.tools
    other.tools_cache = self.tools_cache
    
    return other
  
  #//-------------------------------------------------------//
  
  def   __addTool( self, tool_name, options ):
    
    options_ref = options.getHashRef()
    
    try:
      return self.tools_cache[ tool_name ][ options_ref ]
    except KeyError:
      pass
    
    tool, tool_names, tool_options = self.tools.getTool( tool_name, options )
    
    tool = ToolWrapper( tool, self.project, tool_options )
    
    attrs = self.__dict__
    
    for name in tool_names:
      if name not in attrs:
        attrs[ name ] = tool
        name_tools = self.tools_cache.setdefault( name, {} )
        name_tools[ options_ref ] = tool
    
    return tool
  
  #//-------------------------------------------------------//
  
  def   __getattr__( self, name ):
    
    options = self.project.options
    
    tool = BuiltinTool( options )
    tool_method = getattr( tool, name, None )
    if tool_method and isinstance( tool_method, (types.FunctionType, types.MethodType) ):
      return BuilderWrapper( tool_method, self.project, options )
    
    return self.__addTool( name, options )
  
  #//-------------------------------------------------------//
  
  def __getitem__( self, name ):
    return getattr( self, name )
  
  #//-------------------------------------------------------//
  
  def   Tools( self, *tool_names, **kw ):
    
    tools_path = kw.pop('tools_path', [])
    options = kw.pop( 'options', None )
    
    self.tools.loadTools( tools_path )
    
    if options is None:
      options = self.project.options
    
    if kw:
      options = options.override()
      options.update( kw )
    
    self.tools.loadTools( options.tools_path.get() )
    
    tools = [ self.__addTool( tool_name, options ) for tool_name in tool_names ]
    
    return tools
  
  #//-------------------------------------------------------//
  
  def   Tool( self, tool_name, **kw ):
    return self.Tools( tool_name, **kw )[0]
  
  #//-------------------------------------------------------//
  
  def   AddTool( self, tool_class, tool_names = tuple() ):
    self.tools.addTool( tool_class, tool_names )
    
    return self.__addTool( tool_class, self.project.options )

#//===========================================================================//

#noinspection PyProtectedMember,PyAttributeOutsideInit
class Project( object ):
  
  def   __init__( self, options, targets ):
    
    self.targets = targets
    self.options = options
    self.scripts_cache = {}
    self.aliases = {}
    self.defaults = []
    
    self.build_manager = BuildManager()
    
    self.tools = ProjectTools( self )
  
  #//-------------------------------------------------------//
  
  def   _override( self ):
    """
    @rtype : Project
    """
    other = super(Project,self).__new__( self.__class__ )
    
    other.targets       = self.targets
    other.scripts_cache = self.scripts_cache
    other.build_manager = self.build_manager
    other.aliases       = self.aliases
    other.defaults      = self.defaults
    other.options       = self.options.override()
    other.tools         = self.tools._override( other )
    
    return other
  
  #//-------------------------------------------------------//
  
  def   __getattr__( self, attr ):
    if attr == 'script_locals':
      self.script_locals = self.__getSciptLocals()
      return self.script_locals
    
    raise AttributeError("No attribute '%s'" % (attr,) )
    
  #//-------------------------------------------------------//
  
  def   __getSciptLocals( self ):
    
    script_locals = {
      'options'   : self.options,
      'tools'     : self.tools,
      'Tool'      : self.tools.Tool,
      'Tools'     : self.tools.Tools,
      'AddTool'   : self.tools.AddTool,
      'FindFiles' : findFiles
    }
    
    for name in dir(self):
      if name.startswith('_'):
        continue
      
      member = getattr( self, name )
      if isinstance( member, types.MethodType ):
        script_locals.setdefault( name, member )
    
    return script_locals
  
  #//-------------------------------------------------------//
  
  def   FileValue(self, filepath, options = None ):
    if options is None:
      options = self.options
    file_type = FileTimestampValue if options.file_signature == 'timestamp' else FileChecksumValue
    
    return file_type( filepath )
  
  #//-------------------------------------------------------//
  
  def   DirValue( self, filepath ):
    return DirValue( filepath )
  
  #//-------------------------------------------------------//
  
  def   _execScript( self, script, script_locals ):
    
    script = FilePath( script ).abspath()
    
    scripts_cache = self.scripts_cache
    
    script_result = scripts_cache.get( script, None )
    if script_result is not None:
      return script_result

    with Chdir( script.dirname() ):
      script_result = execFile( script, script_locals )
      scripts_cache[ script ] = script_result
      return script_result
  
  #//-------------------------------------------------------//
  
  def   ReadOptions( self, options_file, options = None ):
    
    if options is None:
      options = self.options
    
    script_locals = { 'options': options }
    
    script_locals = self._execScript( options_file, script_locals )
    
    options.update( script_locals )
  
  #//-------------------------------------------------------//
  
  def   Include( self, makefile ):
    
    other = self._override()
    return other._execScript( makefile, self.script_locals )
  
  #//-------------------------------------------------------//
  
  def   AddNodes( self, nodes ):
    self.build_manager.add( nodes )
  
  #//-------------------------------------------------------//
  
  def   SetBuildDir( self, build_dir ):
    self.options.build_dir = os.path.abspath(build_dir)
  
  #//-------------------------------------------------------//
  
  def   Depends( self, nodes, dependencies ):
    for node in toSequence( nodes ):
      node.depends( dependencies )
      self.build_manager.depends( node, node.dep_nodes )
  
  #//-------------------------------------------------------//
  
  def   Alias( self, alias, nodes ):
    for alias, node in itertools.product( toSequence( alias ), toSequence( nodes ) ):
      self.aliases.setdefault( alias, []).append( node )
    
  #//-------------------------------------------------------//
  
  def   Default( self, nodes ):
    for node in toSequence( nodes ):
      self.defaults.append( node )
  
  #//-------------------------------------------------------//
  
  def   AlwaysBuild( self, nodes ):
    null_value = NullValue()
    for node in toSequence( nodes ):
      node.depends( null_value )
  
  #//=======================================================//
  
  def   _getBuildNodes( self ):
    target_nodes = []
    
    try:
      for alias in self.targets:
        target_nodes += self.aliases[ alias ]
    except KeyError as ex:
      raise ErrorProjectUnknownTarget( ex.args[0] )
    
    if not target_nodes:
      target_nodes = self.defaults
    
    if not target_nodes:
      target_nodes = None
    
    return target_nodes
  
  #//=======================================================//
  
  def   Build( self, jobs = None, keep_going = False, verbose = False, build_always = False ):
    brief = not verbose
    
    if not jobs:
      jobs = 0
    else:
      jobs = int(jobs)
    
    if not jobs:
      jobs = cpuCount()
    
    if jobs < 0:
      jobs = 1
    
    elif jobs > 32:
      jobs = 32
    
    build_nodes = self._getBuildNodes()
    
    is_ok = self.build_manager.build( jobs = jobs, keep_going = bool(keep_going), nodes = build_nodes,
                                      brief = brief, build_always = build_always )
    return is_ok
  
  #//=======================================================//
  
  def Clean(self, verbose = False ):
    brief = not verbose
    build_nodes = self._getBuildNodes()
    
    self.build_manager.clear( nodes = build_nodes, brief = brief )
  
  #//=======================================================//
  
  def Status(self, verbose = False ):
    brief = not verbose
    build_nodes = self._getBuildNodes()
    
    is_actual = self.build_manager.status( nodes = build_nodes, brief = brief )
    return is_actual
  
  #//=======================================================//
