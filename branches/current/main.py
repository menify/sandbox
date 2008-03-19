
import os.path

import SCons.Script
import SCons.Tool
import SCons.Util
import SCons.Defaults

import logging
import options
import builtin_options
import setup_init
import utils
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

SCons.Script.AddOption('--h',
                        default = False,
                        dest = 'detailed_help',
                        action = "store_true",
                        help = 'Print a detailed help message.')

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
    
    cpppath_lib = _EnvOptions(env).cpppath_lib.GetList()
    
    prefix = env['INCPREFIX']
    suffix = env['INCSUFFIX'] + ' '
    
    flags = ''
    for p in cpppath_lib:
        flags += prefix + str(p) + suffix
    
    return flags

#//---------------------------------------------------------------------------//

def     _update_env_flags( env ):
    
    env['_AQL_M_CFLAGS']        = lambda target, source, env, for_signature: _EnvOptions(env).cflags.GetList()
    env['_AQL_M_CCFLAGS']       = lambda target, source, env, for_signature: _EnvOptions(env).ccflags.GetList()
    env['_AQL_M_CXXFLAGS']      = lambda target, source, env, for_signature: _EnvOptions(env).cxxflags.GetList()
    env['_AQL_M_LINKFLAGS']     = lambda target, source, env, for_signature: _EnvOptions(env).linkflags.GetList()
    env['_AQL_M_ARFLAGS']       = lambda target, source, env, for_signature: _EnvOptions(env).arflags.GetList()
    
    env['_AQL_M_CPPPATH']       = lambda target, source, env, for_signature: _EnvOptions(env).cpppath.GetList()
    env['_AQL_M_CPPDEFINES']    = lambda target, source, env, for_signature: _EnvOptions(env).cppdefines.GetList()
    env['_AQL_M_LIBPATH']       = lambda target, source, env, for_signature: _EnvOptions(env).libpath.GetList()
    env['_AQL_M_LIBS']          = lambda target, source, env, for_signature: _EnvOptions(env).libs.GetList()
    
    env['_AQL_M_CPPINCFLAGS']   = _cpppath_lib
    
    env['_CPPDEFFLAGS'] = '${_concat(CPPDEFPREFIX, CPPDEFINES, CPPDEFSUFFIX, __env__)}'
    
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
                        tools = options.tools.GetList(),
                        toolpath = options.tools_path.GetList(),
                        options = None,
                        **kw )
    
    _update_env_flags( env )
    
    return env

#//===========================================================================//

def     BuildVariant( options, scriptfile = None, **kw ):
    
    logging.LogLevel( options.log_level.Get() )
    
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
    
    for bv in build_variants.GetList():
        BuildVariant( options = options( build_variant = bv ), scriptfile = scriptfile, **kw )

