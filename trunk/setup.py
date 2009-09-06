
import logging
import utils
import options

_Warning = logging.Warning
_Info = logging.Info

#//===========================================================================//

_site_setup = []
_user_setup = {}
_tools_setup = {}
_tools_post_setup = {}

def     ResetSetup( site_setup = _site_setup,
                    user_setup = _user_setup,
                    tools_setup = _tools_setup,
                    tools_post_setup = _tools_post_setup ):
    if __debug__:
        _Info( "ResetSetup" )
    
    del site_setup[:]
    user_setup.clear()
    tools_setup.clear()
    tools_post_setup.clear()

#//===========================================================================//

def     AddSiteSetup( setup_function, _site_setup = _site_setup, toList = utils.toList ):
    _site_setup.append( setup_function )

def     siteSetup( setup_function ):
    AddSiteSetup( setup_function )
    return setup_function

def     SiteSetup( options, os_env ):
    
    global _site_setup
    
    for f in _site_setup:
        if __debug__:
            _Info( "Site setup: " + f.__name__ )
        f( options = options, os_env = os_env )
    
    UserSetup( options, os_env )

#//===========================================================================//

def     AddUserSetup( setup_id, setup_function, user_setup = _user_setup ):
    user_setup.setdefault( setup_id, [] ).append( setup_function )

def     UserSetup( options, os_env, user_setup = _user_setup ):
    
    for s in options.setup.Value():
        
        if __debug__:
            _Info( "User setup: " + s )
        
        for f in user_setup.get( s, [] ):
            f( options = options, os_env = os_env )

#//===========================================================================//

def     AddToolSetup( tool_name, setup_function, tools_setup = _tools_setup, toList = utils.toList ):
    tools_setup.setdefault( tool_name, [] ).append( setup_function )

def     toolSetup( tool_name ):
    def     addToolSetup( setup_function ):
        AddToolSetup( tool_name, setup_function )
        return setup_function
    
    return addToolSetup

#//===========================================================================//

def     _tool_setup( tool_name, env, tools_setup = _tools_setup ):
    
    options = env.get( 'AQL_OPTIONS' )
    if options is None:
        if __debug__:
            _Warning( "Tool setup: No AQL_OPTIONS in env: " + id(env) )
        return
    
    options.SetEnv( env )
    os_env = env['ENV']
    
    setup_functions = tools_setup.get( tool_name, [] )
    
    if __debug__:
        if not setup_functions:
            #~ _Info( "Setup tool: No setup for tool: " + tool_name )
            return
    
    for f in setup_functions:
        if __debug__:
            _Info( "Tool setup: " + tool_name + ' (' + f.__name__ + ')' )
        
        if f( env = env, options = options, os_env = os_env ):
            break

#//===========================================================================//

def     AddToolPostSetup( tool_name, setup_function, tools_post_setup = _tools_post_setup ):
    tools_post_setup.setdefault( tool_name, [] ).append( setup_function )

def     toolPostSetup( tool_name ):
    def     addToolPostSetup( setup_function ):
        AddToolPostSetup( tool_name, setup_function )
        return setup_function
    
    return addToolPostSetup

#//===========================================================================//

def     _tool_post_setup( tool_name, env, tools_post_setup = _tools_post_setup ):
    
    options = env.get( 'AQL_OPTIONS' )
    if options is None:
        return
    
    options.SetEnv( env )
    os_env = env['ENV']
    
    setup_functions = tools_post_setup.get( tool_name, [] )
    
    if __debug__:
        if not setup_functions:
            #~ _Info( "Tool post setup: No setup for tool: " + tool_name )
            return
    
    for f in setup_functions:
        if __debug__:
            _Info( "Tool post setup: " + tool_name + ' (' + f.__name__ + ')' )
        f( env = env, options = options, os_env = os_env )


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

