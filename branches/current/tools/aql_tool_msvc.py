
import SCons.Tool

#//---------------------------------------------------------------------------//

def     _setup_flags( options ):
    
    if_ = options.If().cc_name['msvc']
    
    if_.debug_symbols['true'].ccflags += '/Z7'
    if_.debug_symbols['true'].linkflags += '/DEBUG'
    
    if_.user_interface['console'].linkflags += '/subsystem:console'
    if_.user_interface['gui'].linkflags += '/subsystem:windows'
    
    if_.link_runtime['shared'].runtime_debugging['false'].ccflags += '/MD'
    if_.link_runtime['shared'].runtime_debugging['true'].ccflags += '/MDd'
    if_.link_runtime['static'].runtime_debugging['false'].threading['single'].ccflags += '/ML'
    if_.link_runtime['static'].runtime_debugging['false'].threading['multi'].ccflags += '/MT'
    if_.link_runtime['static'].runtime_debugging['true'].threading['single'].ccflags += '/MLd'
    if_.link_runtime['static'].runtime_debugging['true'].threading['multi'].ccflags += '/MTd'
    
    if_.cc_ver.ge(7).cc_ver.lt(8).ccflags += '/Zc:forScope /Zc:wchar_t'
    
    if_.optimization['speed'].cc_ver.ge(8).ccflags += '/O2'
    if_.optimization['speed'].cc_ver.lt(8).ccflags += '/Ogity /O2 /Gr /GF /Gy'
    if_.optimization['speed'].linkflags += '/OPT:REF /OPT:ICF'
    
    if_.optimization['size'].cc_ver.ge(8).ccflags += '/O1'
    if_.optimization['size'].cc_ver.lt(8).ccflags += '/Ogisy /O1 /Gr /GF /Gy'
    if_.optimization['size'].linkflags += '/OPT:REF /OPT:ICF'
    
    if_.optimization['off'].ccflags += '/Od'
    
    if_.inlining['off'].ccflags += '/Ob0'
    if_.inlining['on'].ccflags += '/Ob1'
    if_.inlining['full'].ccflags += '/Ob2'
    
    if_.rtti['true'].cxxflags += '/GR'
    if_.rtti['false'].cxxflags += '/GR-'
    
    if_.exception_handling['true'].cxxflags += '/EHsc'
    if_.exception_handling['false'].cxxflags += '/EHs- /EHc-'
    
    if_.keep_asm['true'].ccflags += '/Fa${TARGET.base}.asm /FAs'
    
    if_.warning_level[0].ccflags += '/w'
    if_.warning_level[1].ccflags += '/W1'
    if_.warning_level[2].ccflags += '/W2'
    if_.warning_level[3].ccflags += '/W3'
    if_.warning_level[4].ccflags += '/Wall /Wp64'
    
    if_.warnings_as_errors['on'].ccflags += '/WX'
    
    if_.linkflags += '/INCREMENTAL:NO'

#//---------------------------------------------------------------------------//

def     _try_tools( env, options, check_exists_only = 0 ):
    
    if (options.cc_name != '') and (options.cc_name != 'msvc'):
        return None
    
    if options.cc_ver != '':
        env['MSVS_VERSION'] = str(options.cc_ver)
    
    _Tool = SCons.Tool.Tool
    
    for t in ('msvc', 'mslink', 'mslib'):
        tool = _Tool( t )
        if not tool.exists( env ):
            return 0
        
        if not check_exists_only:
            tool( env )
    
    return 1

#//---------------------------------------------------------------------------//

def     generate( env ):
    
    options = env['AQL_OPTIONS']
    
    _try_tools( env, options )
    
    options.cc_name = 'msvc'
    options.cc_ver = env['MSVS_VERSION']
    options.target_os = 'windows'
    options.target_os_release = ''
    options.target_os_version = ''
    options.target_machine = 'i386'
    options.target_cpu = ''
    
    #~ _setup_flags( options )
    


#//---------------------------------------------------------------------------//

def     exists( env ):
    return _try_tools( env, env['AQL_OPTIONS'] )

