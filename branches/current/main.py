
import os.path

import SCons.Script
import SCons.Tool

import logging
import options
import builtin_options
import setup
import utils

#//===========================================================================//

_Info = logging.Info

_BuiltinOptions = builtin_options.BuiltinOptions

_Setup = setup.Setup

_EnvOptions = options.EnvOptions

_ARGUMENTS = SCons.Script.ARGUMENTS
_Environment = SCons.Script.Environment

#//-------------------------------------------------------//

utils.AddToolPath( os.path.normpath( os.path.dirname( __file__ ) + '/tools' ) )

#//===========================================================================//

def     _flags( env, name ):
    return str( _EnvOptions( env )[ name ] )

#//---------------------------------------------------------------------------//

def     _cflags( target, source, env, for_signature ):      return _flags( env, 'cflags' )
def     _ccflags( target, source, env, for_signature ):     return _flags( env, 'ccflags' )
def     _cxxflags( target, source, env, for_signature ):    return _flags( env, 'cxxflags' )
def     _linkflags( target, source, env, for_signature ):   return _flags( env, 'linkflags' )
def     _arflags( target, source, env, for_signature ):   return _flags( env, 'arflags' )

#//---------------------------------------------------------------------------//

def     _path( env, path_name ):
    _Dir = env.Dir
    
    path = []
    
    for p in _EnvOptions( env )[ path_name ].Get():
        path.append( _Dir( p ).srcnode() )
    
    return path

#//---------------------------------------------------------------------------//

def     _build_cpppath( target, source, env, for_signature ):
    
    _Dir = env.Dir
    
    path = []
    
    for p in _EnvOptions( env ).build_cpppath.Get():
        d =_Dir( p )
        path.append( d )
        path.append( d.srcnode() )
    
    return path
    
def     _cpppath( target, source, env, for_signature ):         return _path( env, 'cpppath' )
def     _libpath( target, source, env, for_signature ):         return _path( env, 'libpath' )

def     _cpppath_lib( target, source, env, for_signature ):
    
    cpppath_lib = _EnvOptions( env ).cpppath_lib.Get()
    
    prefix = env['INCPREFIX']
    suffix = env['INCSUFFIX'] + ' '
    
    flags = ''
    for p in cpppath_lib:
        flags += prefix + p + suffix
    
    return flags

def     _libs( target, source, env, for_signature ):            return _EnvOptions( env ).libs.Get()
def     _cppdefines( target, source, env, for_signature ):      return _EnvOptions( env ).cppdefines.Get()

#//---------------------------------------------------------------------------//

def     _update_env_flags( env ):
    
    env['_CPPDEFFLAGS'] = '${_concat(CPPDEFPREFIX, CPPDEFINES, CPPDEFSUFFIX, __env__)}'
    
    env['_AQL_M_CFLAGS'] = _cflags
    env['_AQL_M_CCFLAGS'] = _ccflags
    env['_AQL_M_CXXFLAGS'] = _cxxflags
    env['_AQL_M_LINKFLAGS'] = _linkflags
    env['_AQL_M_ARFLAGS'] = _arflags
    env['_AQL_M_CPPPATH'] = _cpppath
    env['_AQL_M_BUILD_CPPPATH'] = _build_cpppath
    env['_AQL_M_CPPINCFLAGS'] = _cpppath_lib
    env['_AQL_M_CPPDEFINES'] = _cppdefines
    env['_AQL_M_LIBPATH'] = _libpath
    env['_AQL_M_LIBS'] = _libs
    
    env.Append( CFLAGS = [ "$_AQL_M_CFLAGS"],
                CCFLAGS = ["$_AQL_M_CCFLAGS"],
                CXXFLAGS = [ "$_AQL_M_CXXFLAGS" ],
                _CPPINCFLAGS = " $_AQL_M_CPPINCFLAGS",
                CPPPATH = [ "$_AQL_M_BUILD_CPPPATH", "$_AQL_M_CPPPATH" ],
                CPPDEFINES = ["$_AQL_M_CPPDEFINES"],
                LINKFLAGS = ["$_AQL_M_LINKFLAGS"],
                ARFLAGS = ["$_AQL_M_ARFLAGS"],
                LIBPATH = ["$_AQL_M_LIBPATH"],
                LIBS = ["$_AQL_M_LIBS"] )

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

#//---------------------------------------------------------------------------//

def     Build( options = None, scriptfile = None, **kw ):
    
    if options is None:
        options = _BuiltinOptions()
        options.update( _ARGUMENTS )
    
    for bv in options.build_variants.Get():
        env_options = options.Clone()
        env_options.bv = bv
        
        BuildVariant( options = env_options, scriptfile = scriptfile, **kw )

