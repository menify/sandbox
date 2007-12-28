
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

#//---------------------------------------------------------------------------//

def     _path( env, path_name ):
    _Dir = env.Dir
    
    path = []
    
    for p in _EnvOptions( env )[ path_name ].Get():
        path.append( _Dir( p ).srcnode() )
    
    return path

#//---------------------------------------------------------------------------//

def     _cpppath( target, source, env, for_signature ):         return _path( env, 'cpppath' )
def     _libpath( target, source, env, for_signature ):         return _path( env, 'libpath' )

def     _const_cpppath( target, source, env, for_signature ):
    
    const_cpppath = _EnvOptions( env ).const_cpppath.Get()
    
    prefix = env['INCPREFIX']
    suffix = env['INCSUFFIX'] + ' '
    
    flags = ''
    for p in const_cpppath:
        flags += prefix + p + suffix
    
    return flags

def     _libs( target, source, env, for_signature ):            return _EnvOptions( env ).libs.Get()
def     _cppdefines( target, source, env, for_signature ):      return _EnvOptions( env ).cppdefines.Get()

#//---------------------------------------------------------------------------//

def     _link_flags( env ):
    
    env['AQL_F_CFLAGS'] = _cflags
    env['AQL_F_CCFLAGS'] = _ccflags
    env['AQL_F_CXXFLAGS'] = _cxxflags
    env['AQL_F_LINKFLAGS'] = _linkflags
    env['AQL_F_CPPPATH'] = _cpppath
    env['AQL_F_CPPINCFLAGS'] = _const_cpppath
    env['AQL_F_CPPDEFINES'] = _cppdefines
    env['AQL_F_LIBPATH'] = _libpath
    env['AQL_F_LIBS'] = _libs
    
    env.Append( CFLAGS = [ "$AQL_F_CFLAGS"],
                CCFLAGS = ["$AQL_F_CCFLAGS"],
                CXXFLAGS = [ "$AQL_F_CXXFLAGS" ],
                _CPPINCFLAGS = " $AQL_F_CPPINCFLAGS",
                CPPPATH = [ "$AQL_F_CPPPATH" ],
                CPPDEFINES = ["$AQL_F_CPPDEFINES"],
                LINKFLAGS = ["$AQL_F_LINKFLAGS"],
                LIBPATH = ["$AQL_F_LIBPATH"],
                LIBS = ["$AQL_F_LIBS"] )

#//---------------------------------------------------------------------------//

def     Env( options, tools=None, **kw ):
    
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
    
    _link_flags( env )
    
    return env

#//===========================================================================//

def     BuildVariant( options, scriptfile = None, **kw ):
    
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
        
        BuildVariant( options = env_options, scriptfile = scriptfile, **kw.copy() )

