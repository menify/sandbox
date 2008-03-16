
import aql.local_host
import aql.utils
import aql.setup

#//---------------------------------------------------------------------------//

def     _setup_vc6( options, env, os_env ):
    
    MSVC6DIR = 'd:/bin/development/compilers/vc6'
    VSCOMMONDIR = MSVC6DIR + '/common'
    MSDEVDIR    = MSVC6DIR + '/common/MSDEV98'
    MSVCDIR     = MSVC6DIR + '/vc98'
    
    vc6_env = options.If().cc_name['msvc'].cc_ver.ge(6).cc_ver.lt(7).os_env
    
    vc6_env['VSCOMMONDIR'] = PathOption()
    vc6_env['MSDEVDIR'] = PathOption()
    
    vc6_env['VSCOMMONDIR'] = VSCOMMONDIR
    vc6_env['MSDEVDIR'] = MSDEVDIR
    vc6_env['PATH'] += MSDEVDIR + '/bin'
    vc6_env['PATH'] += MSVCDIR + '/bin'
    vc6_env['PATH'] += VSCOMMONDIR + '/tools'
    vc6_env['INCLUDE'] += MSVCDIR + '/ATL/INCLUDE'
    vc6_env['INCLUDE'] += MSVCDIR + '/INCLUDE'
    vc6_env['INCLUDE'] += MSVCDIR + '/MFC/INCLUDE'
    vc6_env['LIB'] += MSVCDIR + '/LIB'
    vc6_env['LIB'] += MSVCDIR + '/MFC/LIB'
    

#//---------------------------------------------------------------------------//

def     _setup_msvc_psdk( options, env, os_env, getShellScriptEnv = aql.utils.getShellScriptEnv ):
    
    getShellScriptEnv( os_env, "d:/bin/development/psdk/SetEnv.Bat /XP32  /RETAIL" )

#//---------------------------------------------------------------------------//

def     _setup_vc71( options, env, os_env ):
    
    MSVC71DIR = 'd:/bin/development/compilers/VCToolkit'
    
    vc71_env = options.If().cc_name['msvc'].cc_ver.ge(7).cc_ver.lt(8).os_env
    
    vc71_env['PATH'] += MSVC71DIR + '/bin'
    vc71_env['INCLUDE'] += MSVCDIR + '/include'
    vc71_env['LIB'] += MSVCDIR + '/include'
    
    _setup_msvc_psdk( vc71_env )

#//---------------------------------------------------------------------------//

def     _setup_vc8( options, env, os_env ):
    _GetShellScriptEnv( os_env, "%VS80COMNTOOLS%vsvars32.bat" )
    
    _setup_msvc_psdk( options )

#//---------------------------------------------------------------------------//

def     setup_msvc( options, os_env, env ):
    
    if options.cc_name.isSetNotTo( 'msvc' ):
        return
    
    if options.target_os.isSetNotTo( 'windows' ):
        return
    
    if options.cc_ver.isNotSetOr( 8 ):
        _setup_vc8( options )
    
    elif options.cc_ver == '7':
        _setup_vc71( options )
    
    elif options.cc_ver == '6':
        _setup_vc6( options )

#//===========================================================================//

aql.setup.AddToolSetup( 'aql_tool_msvc', setup_msvc )
