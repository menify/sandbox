
import os.path

import SCons.Script
import SCons.Tool
import SCons.Util

import logging
import options
import builtin_options
import setup
import utils

#//===========================================================================//

_Info = logging.Info

_BuiltinOptions = builtin_options.BuiltinOptions

_Setup = setup.Setup

_EnvLinkedOptions = options.EnvLinkedOptions
_EnvOptions = options.EnvOptions

_ARGUMENTS = SCons.Script.ARGUMENTS
_COMMAND_LINE_TARGETS = SCons.Script.COMMAND_LINE_TARGETS
_Environment = SCons.Script.Environment

_AddMethod = SCons.Util.AddMethod

#//-------------------------------------------------------//

utils.AddToolPath( os.path.normpath( os.path.dirname( __file__ ) + '/tools' ) )

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
#~ _Environment.AQL_LinkedOptions = _EnvLinkedOptions
#~ _Environment.AQL_Options = _EnvOptions

#//===========================================================================//

def     _cflags( target, source, env, for_signature ):      return str( _EnvLinkedOptions(env).cflags )
def     _ccflags( target, source, env, for_signature ):     return str( _EnvLinkedOptions(env).ccflags )
def     _cxxflags( target, source, env, for_signature ):    return str( _EnvLinkedOptions(env).cxxflags )
def     _linkflags( target, source, env, for_signature ):   return str( _EnvLinkedOptions(env).linkflags )
def     _arflags( target, source, env, for_signature ):     return str( _EnvLinkedOptions(env).arflags )

def     _cpppath( target, source, env, for_signature ):     return _EnvLinkedOptions(env).cpppath.Get()
def     _libpath( target, source, env, for_signature ):     return _EnvLinkedOptions(env).libpath.Get()
def     _libs( target, source, env, for_signature ):        return _EnvLinkedOptions(env).libs.Get()
def     _cppdefines( target, source, env, for_signature ):  return _EnvLinkedOptions(env).cppdefines.Get()

def     _cpppath_lib( target, source, env, for_signature ):
    
    cpppath_lib = _EnvLinkedOptions(env).cpppath_lib.Get()
    
    prefix = env['INCPREFIX']
    suffix = env['INCSUFFIX'] + ' '
    
    flags = ''
    for p in cpppath_lib:
        flags += prefix + str(p) + suffix
    
    return flags

#//---------------------------------------------------------------------------//

def     _update_env_flags( env ):
    
    env['_CPPDEFFLAGS'] = '${_concat(CPPDEFPREFIX, CPPDEFINES, CPPDEFSUFFIX, __env__)}'
    
    env['_AQL_M_CFLAGS'] = _cflags
    env['_AQL_M_CCFLAGS'] = _ccflags
    env['_AQL_M_CXXFLAGS'] = _cxxflags
    env['_AQL_M_LINKFLAGS'] = _linkflags
    env['_AQL_M_ARFLAGS'] = _arflags
    env['_AQL_M_CPPPATH'] = _cpppath
    env['_AQL_M_CPPINCFLAGS'] = _cpppath_lib
    env['_AQL_M_CPPDEFINES'] = _cppdefines
    env['_AQL_M_LIBPATH'] = _libpath
    env['_AQL_M_LIBS'] = _libs
    
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

#//---------------------------------------------------------------------------//

def     Env( options, tools = None, **kw ):
    
    kw['_AQL_OPTIONS'] = options
    
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
    
    env = _Environment( platform = None, tools = tools, toolpath = None, options = None, **kw )
    
    _update_env_flags( env )
    
    return env

#//===========================================================================//

def     BuildVariant( options, scriptfile = None, **kw ):
    
    kw = kw.copy()
    
    if scriptfile is None:
        scriptfile = 'SConscript'
    
    if kw.get('duplicate') is None:
        kw['duplicate'] = 0
    
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
        env_options = options.Clone()
        env_options.bv = bv
        
        BuildVariant( options = env_options, scriptfile = scriptfile, **kw )

