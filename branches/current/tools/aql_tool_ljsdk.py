
import os.path

import SCons.Action
import SCons.Builder
import SCons.Tool
import SCons.Script

import aql.utils
import aql.options

_PrependEnvPath = aql.utils.prependEnvPath
_EnvOptions = aql.options.EnvOptions


def     _menu_parser_emitter( target, source, env ):
    options = _EnvOptions(env)
    options.cpppath += env.Dir( os.path.dirname( str(target[0]) ) )
    
    return ([ '${TARGET.base}.cxx', '${TARGET.base}.h' ], source)

def     _add_menu_parser_builder( env ):
    
    env['LJ_MENU_PARSER_COM'] = [ SCons.Util.CLVar('$LJ_MENU_PARSER_PROG $SOURCE'),
                                  SCons.Script.Delete('${TARGETS[0]}' ),
                                  SCons.Script.Delete('${TARGETS[1]}' ),
                                  SCons.Script.Move('${TARGETS[0]}', '${SOURCE.base}.cpp'),
                                  SCons.Script.Move('${TARGETS[1]}', '${SOURCE.base}.h') ]
    
    env['LJMPCXXPREFIX'] = ''
    env['LJMPCXXSUFFIX'] = ''
    
    ljmp_bld = SCons.Builder.Builder(   action = SCons.Action.Action('$LJ_MENU_PARSER_COM'),
                                        prefix = '$LJMPCXXPREFIX',
                                        suffix = '$LJMPCXXSUFFIX',
                                        src_suffix = '.ini',
                                        ensure_suffix = 1,
                                        single_source = 1,
                                        emitter = _menu_parser_emitter )
    
    env['BUILDERS']['LJMenuParser'] = ljmp_bld
    
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)
    static_obj.add_src_builder('LJMenuParser')
    shared_obj.add_src_builder('LJMenuParser')

#//---------------------------------------------------------------------------//

def     _where_is_program( env, prog ):
    return env.WhereIs( prog ) or SCons.Util.WhereIs( prog )

def     _find_ljsdk( options, env ):
    
    if (options.cc_name != 'gcc') or (options.target_os != 'linux') or (options.target_platform != 'LinuxJava'):
        return None
    
    menuparser_path = _where_is_program( env, 'optionsmenu_parser' )
    if menuparser_path is None:
        return None
    
    menuparser_dirpath = os.path.dirname( menuparser_path )
    
    ljsdk_path = os.path.normpath( os.path.join( menuparser_dirpath, '..' ) )
    
    if menuparser_dirpath != os.path.join( ljsdk_path, 'bin' ):
        return None
    
    _PrependEnvPath( env['ENV'], 'PATH', menuparser_dirpath )
    env['LJ_MENU_PARSER_PROG'] = menuparser_path
    
    return ljsdk_path

#//---------------------------------------------------------------------------//

def     _setup_gcc( options ):
    
    gcc_path = str(options.gcc_path)
    cc_ver = str(options.cc_ver)
    gcc_target = str(options.gcc_target)
    
    cpppath_lib = options.cpppath_lib
    cpppath_lib += gcc_path + '/target/usr/include'
    cpppath_lib += gcc_path + '/target/usr/include/c++/' + cc_ver
    cpppath_lib += gcc_path + '/target/usr/include/c++/' + cc_ver + '/' + gcc_target
    cpppath_lib += gcc_path + '/target/usr/include/libxml2'
    
    libpath = options.libpath
    
    libpath += gcc_path + '/target/lib'
    libpath += gcc_path + '/target/usr/lib'


#//---------------------------------------------------------------------------//

def     generate(env):
    
    options = _EnvOptions(env)
    
    ljsdk_path = _find_ljsdk( options, env )
    if ljsdk_path is None:
        return
    
    ljapi_path = os.path.join( ljsdk_path, 'api', str(options.ljapi) )
    
    env['QTDIR'] = ljsdk_path
    env['QT_LIB'] = 'qte-mt'
    
    cpppath = env['CPPPATH']
    
    env.Tool( 'aql_tool_qt' )
    env['CPPPATH'] = cpppath
    
    cpppath_lib = options.cpppath_lib
    cc_ver = str(options.cc_ver)
    gcc_target = str(options.gcc_target)
    
    options.cpppath_lib += ljapi_path + '/include'
    
    if options.target_machine == 'arm':
        options.libpath += ljapi_path + '/lib'
    
    elif options.target_machine == 'x86':
        options.libpath += ljapi_path + '/lib_x86'
    
    options.libs += [ 'dl', 'ezxsort', 'm', 'dmnative',
                      'aplog', 'ezxsound', 'ezxappbase', 'ezxappsdk', 'pthread' ]
    
    _add_menu_parser_builder( env )
    
    _setup_gcc( options )

#//---------------------------------------------------------------------------//

def exists(env):
    return _find_ljsdk( _EnvOptions(env), env ) is not None
