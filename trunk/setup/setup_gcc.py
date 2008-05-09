
import os

import aql.local_host
import aql.utils
import aql.setup

_prependEnvPath = aql.utils.prependEnvPath

if aql.local_host.os == 'cygwin':
    _drive_d = '/cygdrive/d'
else:
    _drive_d = 'd:'

#//===========================================================================//

def     setup_gcc( options, os_env, env ):
    
    if options.cc_name != 'gcc':
        return 0
    
    #//-------------------------------------------------------//
    
    if options.target_os == 'windows':
        
        cc_path = _drive_d

        if options.cc_ver == '4.2':
            cc_path += '/bin/development/compilers/gcc/mingw_4.2.1_dw2'
            options.gcc_prefix = 'mingw32-'
            options.gcc_suffix = '-dw2'
        
        elif options.cc_ver == '4.1':
            cc_path += '/bin/development/compilers/gcc/mingw'
        
        else:
            return 0
        
        _prependEnvPath( os_env, 'PATH', cc_path + '/bin' )
        
        return 1
    
    #//-------------------------------------------------------//
    
    if (options.target_os == 'cygwin') and (aql.local_host.os == 'cygwin'):
        os_env.update( os.environ )
        return 1
    

#//===========================================================================//

aql.setup.AddToolSetup( 'aql_tool_gcc', setup_gcc )
