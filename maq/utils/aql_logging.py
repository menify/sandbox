
import sys
import traceback

import logging


_logger = None

CRITICAL = logging.CRITICAL
FATAL = CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG


#//---------------------------------------------------------------------------//

def   _init():
    logger = logging.getLogger( "AQL" )
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel( logging.DEBUG )
    logger.addHandler( handler )
    
    global _logger
    _logger = logger

#//---------------------------------------------------------------------------//

def     logLevel( level = None ):
    global _logger
    _logger.setLevel( level )

#//---------------------------------------------------------------------------//

def     logCritical(msg, *args, **kwargs):
    global _logger
    _logger.error( msg, *args, **kwargs )

def     logError(msg, *args, **kwargs):
    global _logger
    _logger.error( msg, *args, **kwargs )

def     logMsg( msg ):
        logger.debug()

def     logWarning( msg ):
    if _log_level > 0:
        print 'AQL: Warning: ***', msg

def     logInfo( msg ):
    if _log_level > 1:
        print 'AQL: Info: ***', msg

def     logDebug( exception, traceback_limit = 50, backtfrom = 2 ):
    if __debug__:
        if _log_level > 2:
            try:
                raise ZeroDivisionError
            except ZeroDivisionError:
                frame = sys.exc_info()[ backtfrom ].tb_frame.f_back
            
            print 'AQL DBG: ***', exception
            traceback.print_stack( frame, traceback_limit )


#//-------------------------------------------------------//

_init()
