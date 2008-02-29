
import sys
import os
import popen2
import re

import SCons.Tool
import SCons.Util

#//===========================================================================//

def     _is_sequence( value, isinstance=isinstance, sequence_types = (list, tuple) ):
    return isinstance( value, sequence_types )

#//===========================================================================//

def     AddToolPath( toolpath ):
    SCons.Tool.DefaultToolpath.insert( 0, toolpath )

#//===========================================================================//

def     GetShellScriptEnv( os_env, script ):
    
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

_AppendPath = SCons.Util.AppendPath
_PrependPath = SCons.Util.PrependPath

def     AppendPath( os_env, names, value, sep = os.pathsep ):
    
    if not _is_sequence(names):
        names = ( names, )
    
    value = os.path.normcase( os.path.normpath( value ) )
    
    for name in names:
        os_env[ name ] = _AppendPath( os_env.setdefault( name, '' ), value, sep )

#//---------------------------------------------------------------------------//

def     PrependPath( os_env, names, value, sep = os.pathsep  ):
    
    if not _is_sequence(names):
        names = ( names, )
    
    value = os.path.normcase( os.path.normpath( value ) )
    
    for name in names:
        os_env[ name ] = _PrependPath( os_env[ name ], value, sep )


