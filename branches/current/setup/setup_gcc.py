
import os

import aql.local_host
import aql.utils
import aql.setup

_prependEnvPath = aql.utils.prependEnvPath

#//===========================================================================//

def     setup_gcc( options, os_env, env ):
    
    if options.cc_name != 'gcc':
        return
    
    #//=======================================================//
    
    if (options.target_os == 'cygwin') and (aql.local_host.os == 'cygwin'):
        os_env.update( os.environ )
    
    #//=======================================================//
    
    elif options.target_os == 'windows':
        
        if options.cc_ver == '4.2':
            cc_path = 'd:/bin/development/compilers/gcc/mingw_4.2.1_dw2'
            options.gcc_prefix = 'mingw32-'
            options.gcc_suffix = '-dw2'
        
        elif options.cc_ver == '4.1':
            cc_path = 'd:/bin/development/compilers/gcc/mingw'
        
        _prependEnvPath( os_env, 'PATH', cc_path + '/bin' )

#//===========================================================================//

aql.setup.AddToolSetup( 'aql_tool_gcc', setup_gcc )
