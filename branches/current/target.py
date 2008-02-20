
import sys
import platform

import version

class   Target:
    
    if sys.platform == 'cygwin':
        os = 'cygwin'
    else:
        os = platform.system().lower()
    
    os_release = platform.release().lower()
    
    os_version = version.Version( platform.version() )
    
    machine = platform.machine().lower()
    
    cpu = platform.processor().lower()
    
    cpu_flags = []
    
    platform = sys.platform.lower()



