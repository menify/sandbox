
import os.path

import SCons.Action
import SCons.Builder
import SCons.Tool
import SCons.Script

import aql

_PrependPath = aql.PrependPath


def     _menu_parser_emitter( target, source, env ):
    return ([ '${TARGET.dir}/.menu/${TARGET.filebase}.cpp', '${TARGET.dir}/.menu/${TARGET.filebase}.h' ], source)

def     _add_menu_parser_builder( env, ljsdk_path ):
    
    env['LJ_MENU_PARSER_COM'] = [ SCons.Util.CLVar('$LJ_MENU_PARSER_PROG $SOURCE'),
                                  SCons.Script.Delete('${TARGETS[0]}' ),
                                  SCons.Script.Delete('${TARGETS[1]}' ),
                                  SCons.Script.Move('${TARGETS[0]}', '${SOURCE.base}.cpp'),
                                  SCons.Script.Move('${TARGETS[1]}', '${SOURCE.base}.h') ]
    
    ljmp_bld = SCons.Builder.Builder(   action = SCons.Action.Action('$LJ_MENU_PARSER_COM'),
                                        suffix = '.cpp',
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

def     _find_ljsdk( env ):
    
    options = env['AQL_OPTIONS']
    
    if (options.cc_name != 'gcc') or (options.target_os != 'linux') or (options.target_platform != 'LinuxJava'):
        return None
    
    menuparser_path = _where_is_program( env, 'optionsmenu_parser' )
    if menuparser_path is None:
        return None
    
    menuparser_dirpath = os.path.dirname( menuparser_path )
    
    ljsdk_path = os.path.normpath( os.path.join( menuparser_dirpath, '..' ) )
    
    if menuparser_dirpath != os.path.join( ljsdk_path, 'bin' ):
        return None
    
    _PrependPath( env['ENV'], 'PATH', menuparser_dirpath )
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
    
    ljsdk_path = _find_ljsdk( env )
    if ljsdk_path is None:
        return
    
    options = env['AQL_OPTIONS']
    ljapi_path = os.path.join( ljsdk_path, 'api', str(options.ljapi) )
    
    env['QTDIR'] = ljsdk_path
    env['QT_LIB'] = 'qte-mt'
    SCons.Tool.Tool( 'qt' )( env )
    
    cpppath_lib = options.cpppath_lib
    cc_ver = str(options.cc_ver)
    gcc_target = str(options.gcc_target)
    
    options.cpppath_lib += ljapi_path + '/include'
    
    if options.target_machine == 'arm':
        options.libpath += ljapi_path + '/lib'
    
    elif options.target_machine == 'x86':
        options.libpath += ljapi_path + '/lib_x86'
    
    options.libs += [ 'dl', 'ezxsort', 'drmfwudaclient', 'janus', 'm',
                  'dmnative', 'ezxjpegutils', 'ezxexif', 'ezxam',
                  'masauf', 'aplog', 'ezxsound', 'ezxappbase', 'pthread' ]
    
    _add_menu_parser_builder( env, ljsdk_path )
    
    _setup_gcc( options )

#//---------------------------------------------------------------------------//

def exists(env):
    return _find_ljsdk( env ) is not None
