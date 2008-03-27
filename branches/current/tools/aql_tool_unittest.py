
import subprocess

#//===========================================================================//

def     _ut_action( target, source, env ):
    
    test_program = source[0].abspath
    
    output = open( target[0].abspath, 'w' )
    try:
        process = subprocess.Popen( test_program, stdout = output, stderr = output )
        
        if process.wait() == 0:
            output.write( "\n-= PASSED =-\n" )
            return 0
        
        else:
            output.write( "\n-= FAILED =-\n" )
            output.close()
            output = open( output.name, 'r' )
            for l in output:
                print l
        
    finally:
        output.close()
        
    
    return 1

#//===========================================================================//

def     _ut_action_str( target, source, env ):
    return 'Testing: ' + str(source[0])

#//===========================================================================//

def generate( env ):
    
    ut_action = env.Action( _ut_action, _ut_action_str )
    
    env['BUILDERS']['UnitTest'] = env.Builder( action = ut_action, suffix='.passed' )

#//===========================================================================//

def exists(env):
    return 1
