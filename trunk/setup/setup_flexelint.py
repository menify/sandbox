
import os.path
import aql.utils
from aql.setup import toolSetup
import aql.local_host

#//---------------------------------------------------------------------------//

@toolSetup('aql_tool_flexelint')
def     setup_flexelint( options, os_env, env ):
    
    if aql.local_host.os == 'cygwin':
        _drive_d = '/cygdrive/d'
    else:
        _drive_d = 'd:'
    
    FLEXELINTDIR = _drive_d + '/bin/development/flexelint'
    FLEXLINT_USER_DIR = os.path.join( os.path.dirname( __file__ ), 'lnt' )
    
    aql.utils.prependEnvPath( os_env, 'PATH', FLEXELINTDIR + '/bin' )
    
    options.lint_flags += '-i' + FLEXELINTDIR + '/lnt'
    options.lint_flags += '-i' + FLEXLINT_USER_DIR
    options.lint_flags += 'common.lnt'
    options.lint_flags += 'msg_format.lnt'
