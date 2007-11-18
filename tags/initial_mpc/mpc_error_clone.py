
import sys
import traceback

class   MPC_Error( StandardError ):
    pass

def     Error( exception ):
    raise MPC_Error( exception )

def     Warning( msg ):
    print '\n', 'MPC Warning: ***', msg, '\n'

def     Info( msg ):
    print 'MPC Information: ***', msg


def     DebugMsg( exception, traceback_limit = 50 ):
    
    if __debug__:
        try:
            raise ZeroDivisionError
        except ZeroDivisionError:
            frame = sys.exc_info()[2].tb_frame.f_back
        
        print '\n', 'MPC DBG: ***', exception, '\n'
        traceback.print_stack( frame, traceback_limit )
