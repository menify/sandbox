
import aql.local_host
import aql.utils
import aql.setup

#//---------------------------------------------------------------------------//

def     setup_msvc( options, os_env, env ):
    
    if (options.cc_name != 'msvc') or (options.target_os != 'windows'):
        return 0
    
    if options.cc_ver == '9':
        aql.utils.getShellScriptEnv( os_env, "%VS90COMNTOOLS%vsvars32.bat" )
        
        return 1
    
    return 0

#//===========================================================================//

aql.setup.AddToolSetup( 'aql_tool_msvc', setup_msvc )
