
import sys
import platform


class   Target:
    
    if sys.platform == 'cygwin':
        os = 'cygwin'
    else:
        os = platform.system()
    
    os_release = platform.release()
    
    os_version = platform.version()
    
    machine = platform.machine()
    
    cpu = platform.processor()
    
    cpu_flags = []


