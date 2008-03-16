
import os.path
import SCons.Tool

import aql.logging

#//---------------------------------------------------------------------------//

def     generate( env,
                  Warning = aql.logging.Warning,
                  Tool = SCons.Tool.Tool ):
    
    toolsets =  (
                    "aql_tool_gcc",
                    "aql_tool_msvc",
                    #~ "aql_tool_bcc"
                )
    
    for tool in toolsets:
        tool = Tool( tool, toolpath = env.get('toolpath', []) )
        
        if tool.exists( env ):
            tool( env )
            return
    
    Warning( "C/C++ toolchain has not been found." )
    
    default_tool_name = os.path.splitext( os.path.basename( __file__ ) )[0]
    env['TOOLS'].remove( default_tool_name )


#//---------------------------------------------------------------------------//

def     exists(env):
    return 1
