
import sys
import os.path
import types

import logging
import options

_Info = logging.Info
_Msg = logging.Msg

_EnvOptions = options.EnvOptions

#//===========================================================================//

_user_setup_module = None

def     _user_module():
    
    global _user_setup_module
    
    if _user_setup_module is None:
        
        sys.path.append( os.path.join( os.path.dirname( __file__ ), 'setup' ) )
        
        import imp
        
        try:
            fp, pathname, description = imp.find_module( 'aql_setup_site' )
            
            try:
                user_mod = imp.load_module( 'aql_setup_site', fp, pathname, description )
                _user_setup_module = user_mod.__dict__
                
                _Msg( "Using setup file: " + user_mod.__file__ )
                
            finally:
                del sys.path[-1]
                if fp: fp.close()
        
        except ImportError, e:
            _user_setup_module = {}
            
            if __debug__:
                _Info( "Module 'aql_setup_site' has been not found...Skipped." )
    
    return _user_setup_module

#//===========================================================================//

def     _tool_setup( self, env ):
    
    user_module = _user_module()
    
    try:
        user_module[ 'SetupTool_' + self.name ]( _EnvOptions( env ), env['ENV'], env )
    
    except (TypeError, KeyError):
        if __debug__:
            _Info( "No setup for tool: " + str(self.name) )

def     _tool_exists( self, env ):
    if self._aql_is_exist is None:
        _tool_setup( self, env )
        self._aql_is_exist = self._aql_exists( env )
    
    return self._aql_is_exist

def     _tool_generate( self, env ):
    if self._aql_is_exist is None:
        _tool_exists( self, env )
    
    self._aql_generate( env )

#//===========================================================================//

def     _init_tool( self, name, toolpath=[], **kw ):
    
    _SCons_Tool_Tool_init( self, name, toolpath, **kw )
    
    self._aql_is_exist = None
    self._aql_generate = self.generate
    self._aql_exists = self.exists
    
    self.exists = lambda env, self = self: _tool_exists( self, env )
    self.generate = lambda env, self = self: _tool_generate( self, env )

#//-------------------------------------------------------//

import SCons.Tool

_SCons_Tool_Tool_init = SCons.Tool.Tool.__init__
SCons.Tool.Tool.__init__ = _init_tool

#//===========================================================================//

def     Setup( options, os_env ):
    
    user_module = _user_module()
    
    common_setup = user_module.get('Setup')
    if common_setup is not None:
        common_setup( options, os_env )
    
    prefix = "Setup_"
    
    for name in options.setup.Get():
        
        function = user_module.get( prefix + name )
        
        if function is not None:
            function( options, os_env )
