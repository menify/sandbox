
import os.path
import glob
import imp

import setup
import logging

_Info = logging.Info
_Msg = logging.Msg
_Error = logging.Error

#//===========================================================================//

_setup_path = []
_setup_modules = []

def     _get_setup_modules( options,
                            isfile = os.path.isfile,
                            isdir = os.path.isdir,
                            path_join = os.path.join,
                            glob = glob.glob ):
    
    global _setup_path
    
    setup_path = options.setup_path.Value()
    
    if setup_path == _setup_path:
        return _setup_modules
    
    setup_modules = []
    
    for p in setup_path:
        
        if isfile( p ):
            if p not in setup_modules:
                setup_modules.append( p )
        
        elif isdir( p ):
            for m in glob( path_join( p, '*.py') ):
                if m not in setup_modules:
                    setup_modules.append( m )
    
    _setup_path = setup_path
    
    return setup_modules

#//===========================================================================//

def     _load_setup_modules( options,
                             ResetSetup = setup.ResetSetup,
                             _basename = os.path.basename,
                             _splitext = os.path.splitext,
                             _dirname = os.path.dirname):
    
    global _setup_modules
    
    setup_modules = _get_setup_modules( options )
    if setup_modules == _setup_modules:
        return
    
    ResetSetup()
    
    for module_file in setup_modules:
        
        module_dir = _dirname( module_file )
        module_name = _splitext( _basename( module_file) )[0]
        
        fp, pathname, description = imp.find_module( module_name, [ module_dir ] )
        
        try:
            user_mod = imp.load_module( module_name, fp, pathname, description )
            
            _Info( "Using setup file: " + user_mod.__file__ )
            
        finally:
            if fp:
                fp.close()
    
    _setup_modules = setup_modules

#//===========================================================================//

def     Init( options, os_env,
              SiteSetup = setup.SiteSetup ):
    
    _load_setup_modules( options )
    
    SiteSetup( options = options, os_env = os_env )
