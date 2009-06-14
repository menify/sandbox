
import re
import subprocess

import aql.setup

def     _get_msvc_version( env, options ):
    os_env = {}
    for k,v in env['ENV'].iteritems():
        os_env[k] = str(v)
    
    cc_ver = None
    target_machine = None
    
    output = subprocess.Popen( 'link.exe /logo', shell=True, stdout=subprocess.PIPE, env = os_env ).stdout.readline().strip()
    match = re.search(r'Microsoft \(R\) Incremental Linker Version (?P<version>[0-9]+\.[0-9]+)', output )
    if match:
        cc_ver = match.group('version')
    
    output = subprocess.Popen( 'cl.exe /logo', shell=True, stderr=subprocess.PIPE, env = os_env ).stderr.readline().strip()
    match = re.search(r'Compiler Version [0-9.]+ for (?P<machine>.+)', output )
    if match:
        target_machine = match.group('machine')
    
    if not cc_ver:
        return
    
    target_os = 'windows'
    target_os_release = ''
    target_os_version = ''
    
    if not target_machine:
        target_machine = 'i386'
    
    target_cpu = ''
    
    options.target_os = target_os
    options.target_os_release = target_os_release
    options.target_os_version = target_os_version
    options.target_machine = target_machine
    options.target_cpu = target_cpu
    
    options.cc_name = 'msvc'
    options.cc_ver = cc_ver


#//---------------------------------------------------------------------------//

def     setup_msvc( options, os_env, env ):
    
    if (options.cc_name != 'msvc') or (options.target_os != 'windows'):
        return 0
    
    if options.cc_ver == '9':
        aql.utils.getShellScriptEnv( os_env, "%VS90COMNTOOLS%vsvars32.bat" )
        return 1
    
    return 0

def     setup_msvc_aql_flags( options, os_env, env ):

    if_ = options.If()
    
    if_.debug_symbols['true'].ccflags += '/Z7'
    if_.debug_symbols['true'].linkflags += '/DEBUG'
    
    if_.user_interface['console'].linkflags += '/subsystem:console'
    if_.user_interface['gui'].linkflags += '/subsystem:windows'
    
    if_.link_runtime['shared'].runtime_debugging['false'].ccflags += '/MD'
    if_.link_runtime['shared'].runtime_debugging['true'].ccflags += '/MDd'
    if_.link_runtime['static'].runtime_debugging['false'].runtime_threading['single'].ccflags += '/ML'
    if_.link_runtime['static'].runtime_debugging['false'].runtime_threading['multi'].ccflags += '/MT'
    if_.link_runtime['static'].runtime_debugging['true'].runtime_threading['single'].ccflags += '/MLd'
    if_.link_runtime['static'].runtime_debugging['true'].runtime_threading['multi'].ccflags += '/MTd'
    
    if_.cc_ver.ge(7).cc_ver.lt(8).ccflags += '/Zc:forScope /Zc:wchar_t'
    
    if_.optimization['speed'].cc_ver.ge(8).occflags += '/O2'
    if_.optimization['speed'].cc_ver.lt(8).occflags += '/Ogity /O2 /Gr /GF /Gy'
    if_.optimization['speed'].olinkflags += '/OPT:REF /OPT:ICF'
    
    if_.optimization['size'].cc_ver.ge(8).occflags += '/O1'
    if_.optimization['size'].cc_ver.lt(8).occflags += '/Ogisy /O1 /Gr /GF /Gy'
    if_.optimization['size'].olinkflags += '/OPT:REF /OPT:ICF'
    
    if_.optimization['off'].occflags += '/Od'
    
    if_.inlining['off'].occflags += '/Ob0'
    if_.inlining['on'].occflags += '/Ob1'
    if_.inlining['full'].occflags += '/Ob2'
    
    if_.rtti['true'].cxxflags += '/GR'
    if_.rtti['false'].cxxflags += '/GR-'
    
    if_.exception_handling['true'].cxxflags += '/EHsc'
    if_.exception_handling['false'].cxxflags += '/EHs- /EHc-'
    
    if_.keep_asm['true'].ccflags += '/Fa${TARGET.base}.asm /FAs'
    
    if_.warning_level[0].ccflags += '/w'
    if_.warning_level[1].ccflags += '/W1'
    if_.warning_level[2].ccflags += '/W2'
    if_.warning_level[3].ccflags += '/W3'
    if_.warning_level[4].ccflags += '/W4'
    
    if_.warnings_as_errors['on'].ccflags += '/WX'
    
    if_.linkflags += '/INCREMENTAL:NO'
    
    _get_msvc_version(env = env, options = options )


#//===========================================================================//

aql.setup.AddToolSetup( 'msvc', setup_msvc )
aql.setup.AddToolPostSetup( 'msvc', setup_msvc_aql_flags )
