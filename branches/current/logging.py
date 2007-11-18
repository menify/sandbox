
import sys
import traceback

_log_level = 1

# 0 - only error messages will be reported
# 1 - only error and warning messages will be reported
# 2 - only error, warning and informational messages will be reported
# 3 - all messages will be reported

def     LogLevel( level = None ):
    global _log_level
    
    previous_level = _log_level
    
    if level is not None:
        _log_level = int(level)
    
    return previous_level

#//-------------------------------------------------------//

class   ErrorException( StandardError ):
    pass

def     Error( exception ):
    raise ErrorException( exception )

def     Msg( msg ):
        print 'AQL: ***', msg

def     Warning( msg ):
    if LogLevel() > 0:
        print '\n', 'AQL Warning: ***', msg, '\n'

def     Info( msg ):
    if LogLevel() > 1:
        print 'AQL Information: ***', msg

def     DebugMsg( exception, traceback_limit = 50 ):
    if __debug__:
        if LogLevel() > 2:
            try:
                raise ZeroDivisionError
            except ZeroDivisionError:
                frame = sys.exc_info()[2].tb_frame.f_back
            
            print '\n', 'AQL DBG: ***', exception, '\n'
            traceback.print_stack( frame, traceback_limit )
