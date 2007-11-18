
import SCons.Tool

#//---------------------------------------------------------------------------//

_tools = ['bcc32', 'ilink32', 'tlib']

#//---------------------------------------------------------------------------//

def     generate( env ):
    
    global _tools
    
    for tool in _tools:
        SCons.Tool.Tool( tool )( env )
    
    env['MPC_TOOLSET'] = 'bcc'
    env['MPC_TOOLSET_VERSION'] = MPC_Version( os.popen( env['CC'] ).readline() )
    env['MPC_TOOLSET_NAME'] = env['MPC_TOOLSET'] + str(env['MPC_TOOLSET_VERSION'])
    
#//---------------------------------------------------------------------------//

def exists( env ):
    global _tools
    
    for tool in _tools:
        if not SCons.Tool.Tool( tool ).exists( env ):
            return 0
    
    return 1
