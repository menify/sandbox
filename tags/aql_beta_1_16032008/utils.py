
import os.path


#//===========================================================================//

def     isSequence( value, isinstance = isinstance, sequence_types = (list, tuple) ):
    return isinstance( value, sequence_types )

def     isDict( value, isinstance = isinstance, dict_types = dict ):
    return isinstance( value, dict_types )

def     isString( value, isinstance = isinstance, string_types = (str, unicode)):
    return isinstance( value, string_types )

#//===========================================================================//

def     toSequence( value, separator = '',
                    isSequence = isSequence,
                    isString = isString ):
    
    if isSequence( value ):
        return value
    
    if value is None:
        return ()
    
    if separator:
        if isString( value ):
            return value.split( separator )
    
    return ( value, )

#//===========================================================================//

def     toList( value,
                isinstance = isinstance,
                list = list,
                tuple = tuple ):
    
    if isinstance( value, list ):
        return value
    
    if isinstance( value, tuple ):
        return list(value)
    
    if value is None:
        return []
    
    return [ value ]

#//===========================================================================//

def     appendToList( values_list, values, unique ):
    if unique:
        for v in values:
            if not v in values_list:
                values_list.append( v )
    else:
        values_list += values

#//===========================================================================//

def     removeFromList( values_list, values ):
    for v in values:
        while 1:
            try:
                values_list.remove( v )
            except ValueError:
                break

#//===========================================================================//

def     getShellScriptEnv( os_env, script ):
    
    import sys
    import os
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

def     normPath( path,
                  _os_path_normpath = os.path.normpath,
                  _os_path_normcase = os.path.normcase ):
    
    return _os_path_normcase( _os_path_normpath( path ) )

#//===========================================================================//

def     prependPath( oldpaths, newpaths, sep = os.pathsep,
                     normPath = normPath,
                     toSequence = toSequence,
                     isSequence = isSequence ):
    
    newpaths = map( normPath, toSequence( newpaths, sep ) )
    
    for p in toSequence( oldpaths, sep ):
        if p:
            p = normPath( p )
            if p not in newpaths:
                newpaths.append( p )
    
    if isSequence( oldpaths ):
        return newpaths
    
    return sep.join( newpaths )

#//===========================================================================//

def appendPath( oldpaths, newpaths, sep = os.pathsep,
                normPath = normPath,
                toSequence = toSequence,
                isSequence = isSequence ):
    
    newpaths = map( normPath, toSequence( newpaths, sep ) )
    
    unique_oldpaths = []
    for p in toSequence( oldpaths, sep ):
        if p:
            p = normPath( p )
            if (p not in newpaths) and (p not in unique_oldpaths):
                unique_oldpaths.append( p )
    
    paths = unique_oldpaths + newpaths
    
    if isSequence( oldpaths ):
        return paths
    
    return sep.join( paths )

#//===========================================================================//

def     appendEnvPath( os_env, names, value, sep = os.pathsep,
                       appendPath = appendPath,
                       toSequence = toSequence ):
    
    for name in toSequence( names ):
        os_env[ name ] = appendPath( os_env.get( name, '' ), value, sep )

#//===========================================================================//

def     prependEnvPath( os_env, names, value, sep = os.pathsep,
                        prependPath = prependPath,
                        toSequence = toSequence ):
    
    for name in toSequence( names ):
        os_env[ name ] = prependPath( os_env.get( name, '' ), value, sep )


