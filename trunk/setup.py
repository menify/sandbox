
import logging
import utils
import options

_Warning = logging.Warning

#//===========================================================================//

_site_setup = []
_user_setup = {}
_tools_setup = {}
_tools_post_setup = {}

def     ResetSetup( site_setup = _site_setup,
                    tools_setup = _tools_setup,
                    tools_post_setup = _tools_post_setup ):
    
    del site_setup[:]
    tools_setup.clear()
    tools_post_setup.clear()

#//===========================================================================//

def     AddSiteSetup( setup_function, _site_setup = _site_setup, toList = utils.toList ):
    _site_setup += toList( setup_function )

def     SiteSetup( options, os_env ):
    
    global _site_setup
    
    for f in _site_setup:
        f( options = options, os_env = os_env )
    
    UserSetup( options, os_env )

#//===========================================================================//

def     AddUserSetup( setup_id, setup_function, _user_setup = _user_setup ):
    AddToolSetup( setup_id, setup_function, _user_setup )

def     UserSetup( options, os_env, _user_setup = _user_setup ):
    
    for s in options.setup.GetList():
        for f in _user_setup.get( s, [] ):
            f( options = options, os_env = os_env )

#//===========================================================================//

def     AddToolSetup( tool_name, setup_function, tools_setup = _tools_setup, toList = utils.toList ):
    
    current_setup_functions = tools_setup.setdefault( tool_name, [] )
    tools_setup[ tool_name ] = current_setup_functions + toList( setup_function )

#//===========================================================================//

def     AddToolPostSetup( tool_name, setup_function, tools_post_setup = _tools_post_setup ):
    AddToolSetup( tool_name, setup_function, tools_post_setup )

#//===========================================================================//

def     _tool_setup( tool_name, env, tools_setup = _tools_setup ):
    
    options = env.get( 'AQL_OPTIONS' )
    if options is None:
        return
    
    options.SetEnv( env )
    os_env = env['ENV']
    
    for f in tools_setup.get( tool_name, [] ):
        f( env = env, options = options, os_env = os_env )

#//===========================================================================//

def     _tool_post_setup( tool_name, env, tools_post_setup = _tools_post_setup ):
    _tool_setup( tool_name, env, tools_post_setup )

#//===========================================================================//

def     _tool_exists( self, env ):
    if self._aql_is_exist is None:
        _tool_setup( self.name, env )
        self._aql_is_exist = self._aql_exists( env )
    
    return self._aql_is_exist

#//===========================================================================//

def     _tool_generate( self, env ):
    if self._aql_is_exist is None:
        if not _tool_exists( self, env ):
            _Warning( "Tool: '%s' has not been found, but it has been added." % (self.name) )
    
    self._aql_generate( env )
    
    _tool_post_setup( self.name, env )

#//===========================================================================//

def     _init_tool( self, name, toolpath = [], **kw ):
    
    _SCons_Tool_Tool_init( self, name, toolpath, **kw )
    
    self._aql_is_exist = None
    self._aql_generate = self.generate
    self._aql_exists = self.exists
    
    self.exists = lambda env, self = self: _tool_exists( self, env )
    self.generate = lambda env, self = self: _tool_generate( self, env )

#//===========================================================================//

import SCons.Tool

_SCons_Tool_Tool_init = SCons.Tool.Tool.__init__
SCons.Tool.Tool.__init__ = _init_tool

