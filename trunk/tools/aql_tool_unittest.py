
import sys
import subprocess

#//===========================================================================//

def     _ut_action( target, source, env ):
    
    test_program = source[0].abspath
    result = 0
    
    try:
        verbose = env['UT_VERBOSE']
    except KeyError:
        verbose = False
    
    output = open( target[0].abspath, 'w' )
    try:
        process = subprocess.Popen( test_program, stdout = output, stderr = output )
        
        if process.wait() == 0:
            output.write( "\n-= PASSED =-\n" )
        
        else:
            output.write( "\n-= FAILED =-\n" )
            result = 1
            verbose = 1
        
        if verbose:
            output.close()
            output = open( output.name, 'r' )
            for l in output:
                sys.stderr.write( l )
            sys.stderr.flush()
        
    finally:
        output.close()
    
    return result

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
