
import os.path

import SCons.Script
import SCons.Tool
import SCons.Util
import SCons.Defaults

import logging
import options
import builtin_options
import setup
import utils
import options_help_generator

import local_host

#//===========================================================================//

_Info = logging.Info

_BuiltinOptions = builtin_options.BuiltinOptions

_Setup = setup.Setup

_EnvOptions = options.EnvOptions

_ARGUMENTS = SCons.Script.ARGUMENTS
_COMMAND_LINE_TARGETS = SCons.Script.COMMAND_LINE_TARGETS
_Environment = SCons.Script.Environment

_AddMethod = SCons.Util.AddMethod

_GenerateOptionsHelp = options_help_generator.GenerateOptionsHelp

#//===========================================================================//

SCons.Script.AddOption('--h', default = False,
                        dest='detailed_help',
                        action="store_true",
                        help='Print a detailed help message.')

_detailed_help = SCons.Script.GetOption('detailed_help')

if _detailed_help:      SCons.Script.SetOption('help', True )

def     _generate_help( options ):
    if SCons.Script.GetOption('help'):
        SCons.Script.HelpFunction( _GenerateOptionsHelp( options, _detailed_help ) )
    
        if not _detailed_help:
            SCons.Script.HelpFunction( "Use --h option for detailed help." )
        
        return True
    
    return False

#//===========================================================================//

SCons.Defaults.DefaultEnvironment( tools = [] )

#//===========================================================================//

import glob

def     _glob( self, pathname ):
    
    build_dir = os.getcwd()
    src_dir = str(self.Dir('.').srcnode())
    
    os.chdir( src_dir )
    
    files = glob.glob( pathname )
    os.chdir( build_dir )
    
    return files

_Environment.Glob = _glob
#~ _Environment.AQL_Options = _EnvOptions

#//===========================================================================//

def     _cpppath_lib( target, source, env, for_signature ):
    
    cpppath_lib = _EnvOptions(env).cpppath_lib.Get()
    
    prefix = env['INCPREFIX']
    suffix = env['INCSUFFIX'] + ' '
    
    flags = ''
    for p in cpppath_lib:
        flags += prefix + str(p) + suffix
    
    return flags

#//---------------------------------------------------------------------------//

def     _update_env_flags( env ):
    
    env['_CPPDEFFLAGS'] = '${_concat(CPPDEFPREFIX, CPPDEFINES, CPPDEFSUFFIX, __env__)}'
    
    env['_AQL_M_CFLAGS']        = lambda target, source, env, for_signature: str( _EnvOptions(env).cflags )
    env['_AQL_M_CCFLAGS']       = lambda target, source, env, for_signature: str( _EnvOptions(env).ccflags )
    env['_AQL_M_CXXFLAGS']      = lambda target, source, env, for_signature: str( _EnvOptions(env).cxxflags )
    env['_AQL_M_LINKFLAGS']     = lambda target, source, env, for_signature: str( _EnvOptions(env).linkflags )
    env['_AQL_M_ARFLAGS']       = lambda target, source, env, for_signature: str( _EnvOptions(env).arflags )
    
    env['_AQL_M_CPPPATH']       = lambda target, source, env, for_signature: _EnvOptions(env).cpppath.Get()
    env['_AQL_M_CPPDEFINES']    = lambda target, source, env, for_signature: _EnvOptions(env).cppdefines.Get()
    env['_AQL_M_LIBPATH']       = lambda target, source, env, for_signature: _EnvOptions(env).libpath.Get()
    env['_AQL_M_LIBS']          = lambda target, source, env, for_signature: _EnvOptions(env).libs.Get()
    
    env['_AQL_M_CPPINCFLAGS']   = _cpppath_lib
    
    env.Append( CFLAGS = [ "$_AQL_M_CFLAGS"],
                CCFLAGS = ["$_AQL_M_CCFLAGS"],
                CXXFLAGS = [ "$_AQL_M_CXXFLAGS" ],
                _CPPINCFLAGS = " $_AQL_M_CPPINCFLAGS",
                CPPPATH = [ "$_AQL_M_CPPPATH" ],
                CPPDEFINES = ["$_AQL_M_CPPDEFINES"],
                LINKFLAGS = ["$_AQL_M_LINKFLAGS"],
                ARFLAGS = ["$_AQL_M_ARFLAGS"],
                LIBPATH = ["$_AQL_M_LIBPATH"],
                LIBS = ["$_AQL_M_LIBS"] )
    
    if local_host.os == 'windows' and local_host.os_version >= "5.1":
        env['MAXLINELENGTH'] = 8191
    else:
        env['MAXLINELENGTH'] = 2047

#//---------------------------------------------------------------------------//

def     Env( options, tools = None, **kw ):
    
    kw['AQL_OPTIONS'] = options
    
    if tools is None:
        tools = options.tools.Get()
    
    os_env = kw.setdefault( 'ENV', {} )
    os_env.setdefault( 'PATH', '' )
    
    try:
        os_env.setdefault( 'TEMP', os.environ['TEMP'] )
        os_env.setdefault( 'TMP', os.environ['TMP'] )
    except KeyError:
        pass
    
    _Setup( options, os_env )
    
    env = _Environment( platform = None,
                        tools = tools,
                        toolpath = options.tools_path.Get(),
                        options = None,
                        **kw )
    
    _update_env_flags( env )
    
    return env

#//===========================================================================//

def     BuildVariant( options, scriptfile = None, **kw ):
    
    kw = kw.copy()
    
    if scriptfile is None:
        scriptfile = 'SConscript'
    
    kw.setdefault( 'duplicate', 0 )
    
    if __debug__:
        _Info( "Build variant: " + str(options.bv) )
    
    env = Env( options, **kw )
    
    kw['build_dir'] = os.path.normpath( str( options.build_dir ) )
    kw['exports'] = [ {'env' : env} ]
    
    env.SConscript( scriptfile, **kw )
    
    bv = str(options.bv)
    aliases = [ bv ]
    bv_aliases = options.build_variants.Aliases()[ bv ]
    
    if bv_aliases:
        aliases += bv_aliases
    
    env.Alias( aliases, kw['build_dir'] )

#//---------------------------------------------------------------------------//

def     Build( options = None, scriptfile = None, **kw ):
    
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
    
    for bv in options.build_variants.Get():
        BuildVariant( options = options( build_variant = bv ), scriptfile = scriptfile, **kw )

