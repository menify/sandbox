
import sys
import os
import os.path
import types

import logging

_Info = logging.Info
_Msg = logging.Msg

def     _GetShellScriptEnv( os_env, script ):
    
    import sys
    import popen2
    import re
    
    os_environ = os.environ
    
    if (sys.platform == "win32"):
        shell = os_environ.get("COMSPEC", "cmd.exe")
        script = 'call ' + script
    else:
        shell = '/bin/sh'
        script = '. ' + script
    
    cmdout, cmdin = popen2.popen2( shell )
    cmdin.write( script + "\n" )
    cmdin.write( "set\n" )
    cmdin.close()
    env = cmdout.readlines()
    cmdout.close()
    
    for arg in env:
        
        match = re.search(r'^\w+=', arg )
        
        if match:
            index = arg.find('=')
            name = arg[:index]
            value = arg[index + 1:].rstrip('\n \t\r')
            
            current = os_environ.get( name )
            if (current is None) or (value != current):
                os_env[ name ] = value

#//===========================================================================//

_os_pathsep = os.pathsep

def     _add_path( os_env, name, value ):
    
    global _os_pathsep
    
    path = os.path.normcase( os_env.get( name, '' ) )
    value = os.path.normcase( os.path.normpath( value ) )
    
    if path.find( _os_pathsep + value + _os_pathsep ) != -1:
        return
    
    if path and (not path.endswith( _os_pathsep )):
        path += _os_pathsep
    
    path += value
    
    os_env[ name ] = path

#//===========================================================================//

_user_setup_module = None

def     _user_module():
    
    global _user_setup_module
    
    if _user_setup_module is None:
        try:
            sys.path.append( os.path.join( os.path.dirname( __file__ ), 'setup' ) )
            import aql_setup_site
            del sys.path[-1]
            
            _Msg( "Using setup file: " + aql_setup_site.__file__ )
            
            # export functions into aql_setup_site module
            _user_setup_module = aql_setup_site.__dict__
            _user_setup_module['GetShellScriptEnv'] = _GetShellScriptEnv
            _user_setup_module['AppendPath'] = _add_path
            
        except ImportError:
            
            if __debug__:
                _Info( "Module 'aql_setup_site' has been not found...Skipped." )
            
            _user_setup_module = {}
    
    return _user_setup_module

#//===========================================================================//

def     _setup_tool( env, tool ):
    
    user_module = _user_module()
    
    try:
        user_module[ 'SetupTool_' + tool ]( env['AQL_OPTIONS'], env, env['ENV'] )
    
    except (TypeError, KeyError):
        if __debug__:
            _Info( "No setup for tool: " + str(tool) )

#//===========================================================================//

def     _Tool( tool, toolpath = [], **kw ):
    
    global _SCons_Tool_Tool
    
    tool = _SCons_Tool_Tool( tool, toolpath, **kw )
    tool.exists = lambda env, name = tool.name, exists = tool.exists: _setup_tool( env, name ) or exists( env )
    
    return tool

#//-------------------------------------------------------//

import SCons.Tool

_SCons_Tool_Tool = SCons.Tool.__dict__['Tool']
SCons.Tool.__dict__['Tool'] = _Tool

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
