
import sys
import os
import os.path
import popen2
import re
import types

import SCons.Tool

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

_os_pathsep = os.pathsep

def     AppendPath( os_env, names, value ):
    
    t = type(names)
    if (t is not types.ListType) and (t is not types.TupleType):
        names = ( names, )
    
    for name in names:
        global _os_pathsep
        
        path = os.path.normcase( os_env.get( name, '' ) )
        value = os.path.normcase( os.path.normpath( value ) )
        
        if path.find( _os_pathsep + value + _os_pathsep ) != -1:
            return
        
        if path and (not path.endswith( _os_pathsep )):
            path += _os_pathsep
        
        path += value
        
        os_env[ name ] = path
