# mpc_toolset_cc
# mpc_deftool_cc


import os.path
import SCons.Tool



#//---------------------------------------------------------------------------//

_Tool = SCons.Tool.Tool

_toolsets = [
                "mpc_tool_gcc"
                #~ "mpc_tool_msvc",
                #~ "mpc_tool_bcc"
            ]

def     _try_tools( env, check_existence_only = 0 ):
    
    for tool in _toolsets:
        tool = _Tool( tool )
        
        if tool.exists( env ):
            if check_existence_only:
                return 1
            
            tool( env )
            return 1
    
    _Warning("C/C++ toolchain has not been found.")
    
    return 0

#//---------------------------------------------------------------------------//

def     generate( env ):
    _try_tools( env )

#//---------------------------------------------------------------------------//

def     exists(env):
    return _try_tools( env, check_existence_only = 1 )
