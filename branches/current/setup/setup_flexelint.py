
import aql.utils
import aql.setup


#//---------------------------------------------------------------------------//

def     setup_flexelint( options, os_env, env ):
    
    FLEXELINTDIR = 'd:/bin/development/code-analyzers/flexlint'
    FLEXLINT_USER_DIR = 'd:/work/settings/flexelint'
    
    aql.utils.prependEnvPath( os_env, 'PATH', FLEXELINTDIR + '/bin' )
    
    #~ os_env['LINT'] = '-i' + FLEXELINTDIR + '/lnt'
    
    if_cc_name = options.If().cc_name
    if_msvc_ver = if_cc_name['msvc'].cc_ver
    if_msvc_ver['6.0'].lint_flags  += 'co-msc60.lnt'
    if_msvc_ver['7.0'].lint_flags  += 'co-msc70.lnt'
    if_msvc_ver['7.1'].lint_flags  += 'co-msc71.lnt'
    if_msvc_ver['8.0'].lint_flags  += 'co-msc80.lnt'
    
    if_cc_name['wcc'].lint_flags   += 'co-wc32.lnt'
    if_cc_name['gcc'].target_os['windows'].lint_flags += 'co-mingw.lnt'
    
    options.lint_flags += '-i' + FLEXLINT_USER_DIR + '/lnt'
    options.lint_flags += 'common.lnt'
    options.lint_flags += 'msg_format.lnt'

#//===========================================================================//

aql.setup.AddToolSetup( 'aql_tool_flexelint', setup_flexelint )
