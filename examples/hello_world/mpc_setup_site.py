
import sys
import os

def     SetupTool_mpc_tool_flexelint( options, env, os_env ):
    
    FLEXELINTDIR = 'd:/bin/development/code-analyzers/flexlint'
    FLEXLINT_USER_DIR = 'd:/work/settings/flexelint'
    
    flint_env = options.os_env
    
    flint_env['PATH'] += FLEXELINTDIR + '/bin'
    
    flint_env['LINT'] = []
    flint_env['LINT'] += '-i' + FLEXELINTDIR + '/lnt'
    
    if_cc_name = options.If().cc_name
    
    if_msvc_ver = if_cc_name['msvc'].cc_ver
    if_msvc_ver['6.0'].lint_flags  += 'co-msc60.lnt'
    if_msvc_ver['7.0'].lint_flags  += 'co-msc70.lnt'
    if_msvc_ver['7.1'].lint_flags  += 'co-msc71.lnt'
    if_msvc_ver['8.0'].lint_flags  += 'co-msc80.lnt'
    
    if_cc_name['wcc'].lint_flags   += 'co-wc32.lnt'
    if_cc_name['mingw'].lint_flags += 'co-mingw.lnt'
    
    options.lint_flags += '-i' + FLEXLINT_USER_DIR + '/lnt'
    options.lint_flags += 'common.lnt'
    options.lint_flags += 'msg_format.lnt'

#//---------------------------------------------------------------------------//

def     SetupTool_mpc_tool_qt( options, env, os_env ):
    
    options = env['MPC_OPTIONS']
    
    QTDIR = 'd:/work/src/lib3party/qt-4.2.2'
    
    qt_env = options.os_env
    
    qt_env['QTDIR'] = PathOption( QTDIR )
    qt_env['PATH'] += QTDIR

#//---------------------------------------------------------------------------//

def     SetupTool_mpc_tool_wxwidgets( options, env, os_env  ):
    
    WXWIDGETSDIR = 'd:/work/src/lib3party/qt-4.2.2/wxwidgets/wxWidgets-2.8.3'
    
    options.os_env['WXWIDGETSDIR'] = PathOption( WXWIDGETSDIR )

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

def     _setup_msvc_psdk( options, env, os_env ):
    
    GetShellScriptEnv( os_env, "d:\\bin\\development\\psdk\\SetEnv.Bat /XP32  /RETAIL" )

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
    GetShellScriptEnv( os_env, "%VS80COMNTOOLS%vsvars32.bat" )
    
    _setup_msvc_psdk( options )

#//---------------------------------------------------------------------------//

def     SetupTool_mpc_tool_msvc( options, env, os_env  ):
    
    if options.cc_name != '' and options.cc_name != 'msvc':
        return
    
    if options.cc_ver == '' or options.cc_ver == '8':
        _setup_vc8( options )
    elif options.cc_ver == '7':
        _setup_vc71( options )
    
    elif options.cc_ver == '6':
        _setup_vc6( options )
    

#//---------------------------------------------------------------------------//

def     SetupTool_mpc_tool_gcc( options, env, os_env  ):
    
    if options.cc_name != '' and options.cc_name != 'gcc':
        return
    
    target_os = str(options.target_os)
    
    if sys.platform == 'cygwin':
        os_env.update( os.environ ) 
    
    elif (target_os == 'windows'):
        _setup_mingw( options, os_env )
    
    #~ elif (target_os == 'avr') or (options.target_cpu == 'avr'):
        #~ _setup_gcc_avr( options, env, os_env )
    

#//---------------------------------------------------------------------------//

def     _setup_mingw( options, os_env ):
    
    if options.cc_ver == '4.1':
        gcc_ver = '4.1.1'
        cc_path='d:/bin/development/compilers/mingw'
        gcc_suffix = ''
    
    if options.cc_ver == '4.2' or options.cc_ver == '':
        gcc_ver = '4.2.1'
        cc_path='d:/bin/development/compilers/mingw_4.2.1_dw2'
        options.gcc_prefix = 'mingw32-'
        gcc_suffix = '-dw2'
        options.gcc_suffix = gcc_suffix
    
    AppendPath( os_env, 'PATH', cc_path + '/bin' )
    
    AppendPath( os_env, 'CPATH', cc_path + '/include' )
    AppendPath( os_env, 'CPATH', cc_path + '/include/c++/' + gcc_ver )
    AppendPath( os_env, 'CPATH', cc_path + '/include/c++/' + gcc_ver + '/mingw32' )
    AppendPath( os_env, 'CPATH', cc_path + '/lib/gcc/mingw32/' + gcc_ver + gcc_suffix + '/include' )
    AppendPath( os_env, 'LIBRARY_PATH', cc_path + '/lib' )
    


#//---------------------------------------------------------------------------//

#~ def     _setup_gcc_avr( options, env, os_env ):
    
    #~ avr_dir = 'd:/bin/development/compilers/WinAVR'
    #~ cc_path = avr_dir + '/avr'
    #~ gcc_ver = '4.1.1'
    
    #~ gcc_env = options.os_env
    #~ gcc_env['PATH'] += cc_path + '/bin'
    #~ gcc_env['PATH'] += avr_dir + '/bin'
    #~ gcc_env['PATH'] += avr_dir + '/utils/bin'
    
    #~ gcc_env['CPATH'] += cc_path + '/include'
    #~ gcc_env['CPATH'] += cc_path + '/include/avr'
    #~ gcc_env['CPATH'] += cc_path + '/include/util'
    #~ gcc_env['CPATH'] += avr_dir + '/lib/gcc/avr' + gcc_ver + '/include'
    #~ gcc_env['LIBRARY_PATH'] += cc_path + '/lib'
    

#//---------------------------------------------------------------------------//

def     Setup_user1( options, os_env ):
    print "Setup_user1"

def     Setup_user2( options, os_env ):
    print "Setup_user2"

#//---------------------------------------------------------------------------//

def     Setup( options, os_env ):
    pass
    #~ print "SetupCommon"
