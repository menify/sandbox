
import sys
import traceback

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
    if _log_level > 0:
        print 'AQL: Warning: ***', msg

def     Info( msg ):
    if _log_level > 1:
        print 'AQL: Info: ***', msg

def     DebugMsg( exception, traceback_limit = 50, backtfrom = 2 ):
    if __debug__:
        if _log_level > 2:
            try:
                raise ZeroDivisionError
            except ZeroDivisionError:
                frame = sys.exc_info()[ backtfrom ].tb_frame.f_back
            
            print 'AQL DBG: ***', exception
            traceback.print_stack( frame, traceback_limit )
