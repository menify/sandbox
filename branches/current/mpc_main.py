
import os.path

import SCons.Script
import SCons.Tool

import logging
import options
import builtin_options
import setup

#//===========================================================================//

_Info = logging.Info

_BuiltinOptions = builtin_options.BuiltinOptions

_Setup = setup.Setup

_EnvOptions = options.EnvOptions

_ARGUMENTS = SCons.Script.ARGUMENTS
_Environment = SCons.Script.Environment

#//-------------------------------------------------------//

def     AddToDefaultToolPath( toolpath ):
    SCons.Tool.DefaultToolpath.insert( 0, toolpath )

AddToDefaultToolPath( os.path.normpath( os.path.dirname( __file__ ) + '/tools' ) )

#//===========================================================================//

def     _flags( env, name ):
    return str( _EnvOptions( env )[ name ] )

#//---------------------------------------------------------------------------//

def     _cflags( target, source, env, for_signature ):      return _flags( env, 'cflags' )
def     _ccflags( target, source, env, for_signature ):     return _flags( env, 'ccflags' )
def     _cxxflags( target, source, env, for_signature ):    return _flags( env, 'cxxflags' )
def     _linkflags( target, source, env, for_signature ):   return _flags( env, 'linkflags' )

#//---------------------------------------------------------------------------//

def     _link_flags( env ):
    
    env['MPC_CFLAGS'] = _cflags
    env['MPC_CCFLAGS'] = _ccflags
    env['MPC_CXXFLAGS'] = _cxxflags
    env['MPC_LINKFLAGS'] = _linkflags
    
    env.AppendUnique( CFLAGS = "$MPC_CFLAGS",
                      CCFLAGS = "$MPC_CCFLAGS",
                      CXXFLAGS = "$MPC_CXXFLAGS",
                      LINKFLAGS = "$MPC_LINKFLAGS" )

#//---------------------------------------------------------------------------//

def     Env( options, tools=None, **kw ):
    
    kw['MPC_OPTIONS'] = options
    
    if tools is None:
        tools = [ 'aql_deftool_cc' ]
    
    os_env = kw.setdefault( 'ENV', {} )
    os_env.setdefault( 'PATH', '' )
    os_env.setdefault( 'TEMP', os.environ['TEMP'] )
    os_env.setdefault( 'TMP', os.environ['TMP'] )
    
    _Setup( options, os_env )
    
    env = _Environment( platform = None, tools = tools, toolpath = None, options = None, **kw )
    
    _link_flags( env )
    
    return env

#//===========================================================================//

def     BuildVariant( scriptfile, options, **kw ):
    
    if kw.get('duplicate') is None:
        kw['duplicate'] = 0
    
    if __debug__:
        _Info( "Build variant: " + str(options.bv) )
    
    env = Env( options, **kw )
    
    kw['build_dir'] = os.path.normpath( str( options.build_dir ) )
    kw['exports'] = [ {'env' : env} ]
    
    env.SConscript( scriptfile, **kw )

#//---------------------------------------------------------------------------//

def     Build( scriptfile, options = None, **kw ):
    
    if options is None:
        options = _BuiltinOptions()
        
        bvs = options.build_variants
        bvs.AddAliases( 'all', bvs.AllowedValues() )
        
        options.update( _ARGUMENTS )
    
    else:
        bvs = options.build_variants
        bvs.AddAliases( 'all', bvs.AllowedValues() )
    
    
    for bv in bvs.Get():
        env_options = options.Clone()
        env_options.bv = bv
        
        BuildVariant( scriptfile, env_options, **kw.copy() )

