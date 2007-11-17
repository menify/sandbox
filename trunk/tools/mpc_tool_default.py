# mpc_toolset_cc

import os.path

import SCons.Tool

_Tool = SCons.Tool.Tool

#//---------------------------------------------------------------------------//

def     _try_tool( env, tool ):
    
    tool = _Tool( tool )
    
    if tool.exists( env ):
        tool( env )
        return 1
    
    return 0

#//---------------------------------------------------------------------------//

def     generate( env ):
    
    toolsets =  [
                    "mpc_tool_gcc",
                    "mpc_tool_msvc",
                    "mpc_tool_bcc"
                ]
    
    for tool in toolsets:
        if _try_tool( env, tool ):
            break

#//---------------------------------------------------------------------------//

def     exists(env):
    return 1
