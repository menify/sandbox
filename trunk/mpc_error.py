
import sys
import traceback


_log_level = 1

# 0 - only error messages will be reported
# 1 - only error and warning messages will be reported
# 2 - only error, warning and informational messages will be reported
# 3 - all messages will be reported

def     LogLevel( level ):
    _log_level = int(level)

class   MPC_Error( StandardError ):
    pass

def     Error( exception ):
    raise MPC_Error( exception )

def     Warning( msg ):
    if log_level > 0:
        print '\n', 'MPC Warning: ***', msg, '\n'

def     Info( msg ):
    if log_level > 1:
        print 'MPC Information: ***', msg

def     DebugMsg( exception, traceback_limit = 50 ):
    if __debug__:
        if log_level > 2:
            try:
                raise ZeroDivisionError
            except ZeroDivisionError:
                frame = sys.exc_info()[2].tb_frame.f_back
            
            print '\n', 'MPC DBG: ***', exception, '\n'
            traceback.print_stack( frame, traceback_limit )
