import aql.utils
from aql.setup import toolPostSetup

#//---------------------------------------------------------------------------//

@toolPostSetup('aql_tool_msvc')
def     _setup_flags( options, os_env, env ):

    if_ = options.If().cc_name['msvc']
    
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
