
import os

import aql.local_host
import aql.utils
import aql.setup

if aql.local_host.os == 'cygwin':
    _drive = '/cygdrive/c'
else:
    _drive = 'c:'

#//===========================================================================//

def     setup_gcc( options, os_env, env ):
    
    if options.cc_name != 'gcc':
        return False
    
    #//-------------------------------------------------------//
    
    if options.target_os == 'windows':
        
        cc_path = _drive

        if options.cc_ver == '4.4':
            cc_path += '/bin/mingw_4.4.0'
            options.gcc_prefix = 'mingw32-'
            options.gcc_suffix = ''
        
        else:
            return False
        
        aql.utils.prependEnvPath( os_env, 'PATH', cc_path + '/bin' )
        
        return True
    
    #//-------------------------------------------------------//
    
    os_env.update( os.environ )
    return 1
    

#//===========================================================================//

def     _setup_flags( options, os_env, env ):
    
    if_ = options.If()
    
    if_.target_os['windows'].user_interface['console'].linkflags += '-Wl,--subsystem,console'
    if_.target_os['windows'].user_interface['gui'].linkflags += '-Wl,--subsystem,windows'
    
    if_.debug_symbols['true'].ccflags += '-g'
    if_.debug_symbols['false'].linkflags += '-Wl,--strip-all'
    
    if_.link_runtime['static'].linkflags += '-static-libgcc'
    if_.link_runtime['shared'].linkflags += '-shared-libgcc'
    
    if_.target_os['windows'].runtime_threading['multi'].ccflags += '-mthreads'
    if_.target_os.ne('windows').runtime_threading['multi'].ccflags += '-pthreads'
    
    if_.optimization['speed'].occflags += '-O3 -ffast-math'
    if_.optimization['size'].occflags += '-Os -ffast-math'
    if_.optimization['off'].occflags += '-O0'
    
    if_.inlining['off'].occflags += '-fno-inline'
    if_.inlining['on'].occflags += '-finline -Wno-inline'
    if_.inlining['full'].occflags += '-finline-functions -Wno-inline'
    
    if_.rtti['true'].cxxflags += '-frtti'
    if_.rtti['false'].cxxflags += '-fno-rtti'
    
    if_.exception_handling['true'].cxxflags += '-fexceptions'
    if_.exception_handling['false'].cxxflags += '-fno-exceptions'
    
    if_.keep_asm['false'].ccflags += '-pipe'
    if_.keep_asm['true'].ccflags += '-fverbose-asm -save-temps'
    if_.keep_asm['true'].target_machine['x86'].ccflags += '-masm=intel'
    
    
    if_.warning_level[0].ccflags += '-w'
    if_.warning_level[2].ccflags += '-Wall'
    if_.warning_level[3].ccflags += '-Wall -Wextra -Wfloat-equal -Wundef -Wshadow -Wredundant-decls'
    if_.warning_level[4].ccflags += '-Wall -Wextra -Wfloat-equal -Wundef -Wshadow -Wredundant-decls'
    #~ if_.warning_level[4].cxxflags += '-Weffc++'
    
    if_.warning_level[4].cc_ver.ge(4).ccflags += '-Wfatal-errors'
    
    if_.warnings_as_errors['on'].ccflags += '-Werror'
    
    if_profiling_true = if_.profiling['true']
    if_profiling_true.ccflags += '-pg'
    if_profiling_true.linkflags += '-pg'
    if_profiling_true.linkflags -= '-Wl,--strip-all'

#//===========================================================================//

aql.setup.AddToolSetup( 'aql_tool_gcc', setup_gcc )
aql.setup.AddToolPostSetup( 'aql_tool_gcc', _setup_flags )
