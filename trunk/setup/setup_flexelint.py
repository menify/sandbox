
import os.path
import aql.utils
import aql.setup
import aql.local_host

#//---------------------------------------------------------------------------//

if aql.local_host.os == 'cygwin':
    _drive_d = '/cygdrive/d'
else:
    _drive_d = 'd:'

def     setup_flexelint( options, os_env, env ):
    
    FLEXELINTDIR = _drive_d + '/bin/development/flexelint'
    FLEXLINT_USER_DIR = os.path.join( os.path.dirname( __file__ ), 'lnt' )
    
    aql.utils.prependEnvPath( os_env, 'PATH', FLEXELINTDIR + '/bin' )
    
    options.lint_flags += '-i' + FLEXELINTDIR + '/lnt'
    options.lint_flags += '-i' + FLEXLINT_USER_DIR
    options.lint_flags += 'common.lnt'
    options.lint_flags += 'msg_format.lnt'

#//===========================================================================//

aql.setup.AddToolSetup( 'aql_tool_flexelint', setup_flexelint )
