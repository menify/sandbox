
import SCons.Tool

#//---------------------------------------------------------------------------//

_tools = ['bcc32', 'ilink32', 'tlib']

#//---------------------------------------------------------------------------//

def     generate( env ):
    
    global _tools
    
    for tool in _tools:
        SCons.Tool.Tool( tool )( env )
    
#//---------------------------------------------------------------------------//

def exists( env ):
    global _tools
    
    for tool in _tools:
        if not SCons.Tool.Tool( tool ).exists( env ):
            return 0
    
    return 1
