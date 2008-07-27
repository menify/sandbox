
import sys
import os.path
import subprocess

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
import utils

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

#//===========================================================================//

def     _findFiles( env, path, pattern, recursive = True ):
    
    root = env.Dir('.').srcnode().abspath
    return utils.findFiles( root, path, pattern, recursive )

#//===========================================================================//

def     _add_aql_methods( env ):
    env.AddMethod( _findFiles, 'aqlFindFiles' )
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

def     _start_shell( env, options ):
    
    os_env = env['ENV'].copy()
    os_env.update( os.environ )
    
    utils.prependEnvPath( os_env, 'PATH', env['ENV']['PATH'] )
    
    path = os_env['PATH']
    
    shell = os_env.get('SHELL')
    if not shell or not env.WhereIs( shell, path ):
        shell = env.subst('$SHELL')
    
    wait_shell = True
    
    title = str(options.target)
    
    if local_host.os == 'windows':
        start_cmd = 'start ' + shell + ' /k title ' + title
        wait_shell = False
    
    else:
        termimal = os_env.get('TERM')
        
        if termimal and env.WhereIs( termimal, path ):
            start_cmd = termimal
            wait_shell = False
        
        else:
            start_cmd = shell
    
    p = subprocess.Popen( start_cmd, env = os_env, shell = True )
    if wait_shell:
        os.waitpid( p.pid, 0 )
    
    sys.exit()

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
    
    env.SConscript( scriptfile, **kw )
    
    if 'shell' in _COMMAND_LINE_TARGETS:
        _start_shell( env, options )
    
    return env

#//---------------------------------------------------------------------------//

def     Build( scriptfile, options = None, **kw ):
    
    if options is None:
        options = _BuiltinOptions()
        options.update( _ARGUMENTS )
    
    if _generate_help( options ):
        return
    
    for bv in options.build_variants.Value():
        BuildVariant( options = options( build_variant = bv ), scriptfile = scriptfile, **kw )

#//===========================================================================//

_add_cmdline_options()
_add_hook_to_builder_get_prefix()
_set_scons_perfomance_settings()

