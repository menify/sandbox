
import os.path

import SCons.Script
import SCons.Tool
import SCons.Util
import SCons.Defaults
import SCons.Builder

import logging
import options
import builtin_options
import setup_init
import options_help_generator

import local_host

#//===========================================================================//

_Info = logging.Info

_BuiltinOptions = builtin_options.BuiltinOptions

_Setup = setup_init.Init

_EnvOptions = options.EnvOptions

_ARGUMENTS = SCons.Script.ARGUMENTS
_COMMAND_LINE_TARGETS = SCons.Script.COMMAND_LINE_TARGETS
_Environment = SCons.Script.Environment

_AddMethod = SCons.Util.AddMethod

_GenerateOptionsHelp = options_help_generator.GenerateOptionsHelp

#//===========================================================================//

_detailed_help = 0

def     _add_cmdline_options():
    SCons.Script.AddOption( '--h',
                            default = False,
                            dest = 'aql_detailed_help',
                            action = "store_true",
                            help = 'Print a detailed help message.' )
    
    global _detailed_help
    _detailed_help = SCons.Script.GetOption('aql_detailed_help')
    
    if _detailed_help:
        SCons.Script.SetOption('help', True )

#//-------------------------------------------------------//

def     _generate_help( options ):
    if SCons.Script.GetOption('help'):
        SCons.Script.HelpFunction( _GenerateOptionsHelp( options, _detailed_help ) )
        
        if not _detailed_help:
            SCons.Script.HelpFunction( "Use --h option for detailed help." )
        
        return 1
    
    return 0

#//===========================================================================//

def     _set_scons_perfomance_settings():
    SCons.Defaults.DefaultEnvironment( tools = [] )
    SCons.Script.SetOption( 'implicit_cache', 1 )
    SCons.Script.SetOption( 'max_drift', 1 )
    SCons.Script.SetOption( 'num_jobs', os.environ.get('NUMBER_OF_PROCESSORS', 1) )

#//===========================================================================//

def     _src_relative_dir( self, path ):
    
    rel_path = os.path.normcase( os.path.abspath( path ) )
    cur_dir = os.path.normcase( self.Dir('.').srcnode().abspath )
    common_prefix = os.path.commonprefix( [cur_dir, rel_path ] )
    if common_prefix:
        return rel_path[ len( common_prefix ): ].lstrip( os.path.sep )
    
    return path

#//===========================================================================//

import glob

def     _glob( self, path, filter_function = None, absolute_paths = False ):
    
    build_dir = os.getcwd()
    src_dir = self.Dir('.').srcnode().abspath
    
    os.chdir( src_dir )
    
    path = os.path.normcase( os.path.abspath( path ) )
    
    if not absolute_paths:
        src_dir = os.path.normcase( src_dir )
        common_prefix = os.path.commonprefix( [src_dir, path ] )
        if common_prefix:
            path = path[ len( common_prefix ): ].lstrip( os.path.sep )
    
    try:
        files = glob.glob( path )
        
        if filter_function is not None:
            files = filter( filter_function, files )
    finally:
        os.chdir( build_dir )
    
    return files

#//===========================================================================//

def     _add_aql_methods( env ):
    env.AddMethod( _src_relative_dir, 'aqlSrcDir' )
    env.AddMethod( _glob, 'aqlGlob' )
    env.AddMethod( _EnvOptions, 'aqlOptions' )

#//===========================================================================//

def     _add_hook_to_builder_get_prefix():
    
    def     _get_prefix(self, env, sources=[], builder_get_prefix = SCons.Builder.BuilderBase.get_prefix ):
        prefix = builder_get_prefix( self, env, sources )
        return prefix + str(_EnvOptions( env ).prefix)
    
    SCons.Builder.BuilderBase.get_prefix = _get_prefix

#//===========================================================================//

def     _cpppath_lib( target, source, env, for_signature ):
    
    cpppath_lib = _EnvOptions(env).cpppath_lib.Value()
    
    prefix = env['INCPREFIX']
    suffix = env['INCSUFFIX'] + ' '
    
    flags = ''
    for p in cpppath_lib:
        flags += prefix + str(p) + suffix
    
    return flags

#//---------------------------------------------------------------------------//

def     _update_env_flags( env ):
    
    env['_AQL_CFLAGS']        = lambda target, source, env, for_signature: _EnvOptions(env).cflags.Value()
    env['_AQL_CCFLAGS']       = lambda target, source, env, for_signature: _EnvOptions(env).ccflags.Value()
    env['_AQL_CXXFLAGS']      = lambda target, source, env, for_signature: _EnvOptions(env).cxxflags.Value()
    env['_AQL_LINKFLAGS']     = lambda target, source, env, for_signature: _EnvOptions(env).linkflags.Value()
    env['_AQL_ARFLAGS']       = lambda target, source, env, for_signature: _EnvOptions(env).arflags.Value()
    
    env['_AQL_CPPPATH']       = lambda target, source, env, for_signature: _EnvOptions(env).cpppath.Value()
    env['_AQL_CPPDEFINES']    = lambda target, source, env, for_signature: _EnvOptions(env).cppdefines.Value()
    env['_AQL_LIBPATH']       = lambda target, source, env, for_signature: _EnvOptions(env).libpath.Value()
    env['_AQL_LIBS']          = lambda target, source, env, for_signature: _EnvOptions(env).libs.Value()
    
    env['_AQL_CPPINCFLAGS']   = _cpppath_lib
    
    env['_CPPDEFFLAGS'] = '${_concat(CPPDEFPREFIX, CPPDEFINES, CPPDEFSUFFIX, __env__)}'
    
    env.Append( CFLAGS = [ "$_AQL_CFLAGS"],
                CCFLAGS = ["$_AQL_CCFLAGS"],
                CXXFLAGS = [ "$_AQL_CXXFLAGS" ],
                _CPPINCFLAGS = " $_AQL_CPPINCFLAGS",
                CPPPATH = [ "$_AQL_CPPPATH" ],
                CPPDEFINES = ["$_AQL_CPPDEFINES"],
                LINKFLAGS = ["$_AQL_LINKFLAGS"],
                ARFLAGS = ["$_AQL_ARFLAGS"],
                LIBPATH = ["$_AQL_LIBPATH"],
                LIBS = ["$_AQL_LIBS"] )
    
    if local_host.os == 'windows' and local_host.os_version >= "5.1":
        env['MAXLINELENGTH'] = 8191
    else:
        env['MAXLINELENGTH'] = 2047

#//---------------------------------------------------------------------------//

def     Env( options, **kw  ):
    
    os_env = kw.setdefault( 'ENV', {} )
    os_env.setdefault( 'PATH', '' )
    
    for t in ['TEMP', 'TMP']:
        tmp = os.environ.get( t )
        if tmp:
            os_env.setdefault( t, tmp )
    
    kw['AQL_OPTIONS'] = options
    
    _Setup( options, os_env )
    
    env = _Environment( platform = None,
                        tools = options.tools.Value(),
                        toolpath = options.tools_path.Value(),
                        options = None,
                        **kw )
    
    env.Decider( 'MD5-timestamp' )
    env.SourceCode( '.', None )
    
    _update_env_flags( env )
    
    _add_aql_methods( env )
    
    return env

#//===========================================================================//

def     BuildVariant( scriptfile, options, **kw ):
    
    logging.LogLevel( options.log_level.Value() )
    
    kw = kw.copy()
    
    kw.setdefault( 'duplicate', 0 )
    
    if __debug__:
        _Info( "Build variant: " + str(options.bv) )
    
    env = Env( options, **kw )
    
    kw['variant_dir'] = os.path.normpath( str( options.build_dir ) )
    kw['exports'] = [ {'env' : env} ]
    
    if options.lint != 'off':
        SCons.Script.SetOption( 'num_jobs', 1 )
    
    env.SConscript( scriptfile, **kw )
    
    return env

#//---------------------------------------------------------------------------//

def     Build( scriptfile, options = None, **kw ):
    
    if options is None:
        options = _BuiltinOptions()
        options.update( _ARGUMENTS )
    
    if _generate_help( options ):
        return
    
    build_variants = options.build_variants
    builds = []
    for v in _COMMAND_LINE_TARGETS:
        try:
            builds += build_variants.Convert( v )
         
        except logging.ErrorException:
            pass
    
    if builds:
        build_variants.Set( builds )
    
    for bv in build_variants.Value():
        BuildVariant( options = options( build_variant = bv ), scriptfile = scriptfile, **kw )

#//===========================================================================//

_add_cmdline_options()
_add_hook_to_builder_get_prefix()
_set_scons_perfomance_settings()

