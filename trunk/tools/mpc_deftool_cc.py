# mpc_toolset_cc
# mpc_deftool_cc


import os.path
import SCons.Tool

import mpc_log

#//---------------------------------------------------------------------------//

_Warning = mpc_log.Warning
_Tool = SCons.Tool.Tool

#//---------------------------------------------------------------------------//

def     generate( env ):
    
    toolsets =  (
                    "mpc_tool_gcc",
                    "mpc_tool_msvc",
                    #~ "mpc_tool_bcc"
                )
    
    for tool in toolsets:
        tool = _Tool( tool )
        
        if tool.exists( env ):
            tool( env )
            return
    
    _Warning("C/C++ toolchain has not been found.")
    
    default_tool_name = os.path.splitext( os.path.basename( __file__ ) )[0]
    env['TOOLS'].remove( default_tool_name )


#//---------------------------------------------------------------------------//

def     exists(env):
    return 1
