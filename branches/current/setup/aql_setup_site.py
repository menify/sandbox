
import sys
import os

import aql

_Target = aql.Target

_GetShellScriptEnv = aql.GetShellScriptEnv
_PrependPath = aql.PrependPath

#//---------------------------------------------------------------------------//

def     SetupTool_aql_tool_flexelint( options, os_env, env ):
    
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
    
    _GetShellScriptEnv( os_env, "d:/bin/development/psdk/SetEnv.Bat /XP32  /RETAIL" )

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

def     SetupTool_aql_tool_msvc( options, os_env, env ):
    
    if options.cc_name != '' and options.cc_name != 'msvc':
        return
    
    if options.target_os == '':
        options.target_os = _Target.os
    
    if options.target_os != 'windows':
        return
    
    if options.cc_ver == '' or options.cc_ver == '8':
        _setup_vc8( options )
    elif options.cc_ver == '7':
        _setup_vc71( options )
    
    elif options.cc_ver == '6':
        _setup_vc6( options )

#//---------------------------------------------------------------------------//

def     SetupTool_aql_tool_gcc( options, os_env, env ):
    
    if options.cc_name != '' and options.cc_name != 'gcc':
        return
    
    if options.target_os == '':
        options.target_os = _Target.os
    
    if options.target_os == 'cygwin':
        os_env.update( os.environ )
    
    elif options.target_os == 'windows':
        _setup_mingw( options, os_env )
    
    elif options.target_os == 'linux':
        if (options.target_platform == 'LinuxJava'):
            _setup_gcc_lj( options, os_env )
    

#//---------------------------------------------------------------------------//

def     _setup_mingw( options, os_env ):
    
    if options.cc_ver == '4.1':
        cc_path = 'd:/bin/development/compilers/gcc/mingw'
    
    if options.cc_ver == '4.2' or options.cc_ver == '':
        cc_path = 'd:/bin/development/compilers/gcc/mingw_4.2.1_dw2'
        options.gcc_prefix = 'mingw32-'
        options.gcc_suffix = '-dw2'
    
    _PrependPath( os_env, 'PATH', cc_path + '/bin')

#//---------------------------------------------------------------------------//

if _Target.os == 'cygwin':
    _drive = '/cygdrive/d'
else:
    _drive = 'd:'

def     _setup_gcc_lj( options, os_env ):
    
    _PrependPath( os_env, 'PATH', _drive + '/bin/development/compilers/gcc/mvl/MVL-RELEASE-121822007/mvl-environment/bin' )
    
    if options.target_machine == 'arm':
        cc_path = _drive + '/bin/development/compilers/gcc/mvl/MVL-RELEASE-121822007/mvl-environment/moto/common/devkit/arm/v6_vfp_le'
        options.gcc_prefix = 'arm_v6_vfp_le-'
        
        #~ cc_path = drive + '/bin/development/compilers/gcc/lj'
        #~ options.gcc_prefix = 'arm-none-linux-gnueabi-'
        #~ options.ccflags += '-mthumb-interwork -mcpu=arm1136jf-s -mtune=arm1136jf-s -mfpu=vfp'
    
    elif options.target_machine == 'x86':
        cc_path = _drive + '/bin/development/compilers/gcc/mvl/MVL-RELEASE-121822007/mvl-environment/moto/common/devkit/x86/i686-mot-linux-gnu'
        options.gcc_prefix = 'i686-mot-linux-gnu-'
    
    else:
        return
    
    options.exception_handling = 'false'
    options.rtti = 'false'
    options.link_runtime = 'shared'
    
    _PrependPath( os_env, 'PATH', cc_path + '/bin' )

#//---------------------------------------------------------------------------//

def     SetupTool_aql_tool_ljsdk( options, os_env, env ):
    options.ljsdk_path = aql.PathOption( _drive + '/bin/development/SDK/lj/arm' )
