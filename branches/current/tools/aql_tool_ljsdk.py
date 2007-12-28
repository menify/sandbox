
import os.path

import SCons.Action
import SCons.Builder
import SCons.Tool
import SCons.Script

import aql

_AppendPath = aql.AppendPath

def     _menu_parser_emitter( target, source, env ):
    return ([ '${TARGET.dir}/.menu/${TARGET.filebase}.cpp', '${TARGET.dir}/.menu/${TARGET.filebase}.h' ], source)

def     _add_menu_parser_builder( env, ljsdk_path ):
    
    env['LJ_MENU_PARSER_PROG'] = os.path.join( ljsdk_path, 'bin', 'optionsmenu_parser$PROGSUFFIX' )
    
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


def     generate(env):
    
    SCons.Tool.Tool( 'qt' )( env )
    
    options = env['AQL_OPTIONS']
    
    ljsdk_path = str(options.ljsdk_path)
    ljapi_path = ljsdk_path + '/api/' + str(options.ljapi)
    
    if_ = options.If().target_platform['LinuxJava'].target_machine['arm']
    
    #~ if_.const_cpppath += ljsdk_path + '/target/usr/include'
    #~ if_.const_cpppath += ljsdk_path + '/target/usr/include/libxml2'
    #~ if_.const_cpppath += ljapi_path + '/include'
    #~ if_.const_cpppath += ljapi_path + '/dir/kernel_include'
    
    os_env = env['ENV']
    _AppendPath( env['ENV'], 'CPATH', ljsdk_path + '/target/usr/include' )
    _AppendPath( env['ENV'], 'CPATH', ljsdk_path + '/target/usr/include/libxml2' )
    _AppendPath( env['ENV'], 'CPATH', ljapi_path + '/include' )
    _AppendPath( env['ENV'], 'CPATH', ljapi_path + '/dir/kernel_include' )
    
    #~ env.AppendUnique( RPATH = [ ljapi_path + '/lib'] )
    #~ env.AppendUnique( LIBPATH = [ ljapi_path + '/lib'] )
    #~ env.AppendUnique( RPATH = [ ljsdk_path + '/target/lib' ] )
    #~ env.AppendUnique( LIBPATH = [ ljsdk_path + '/target/lib' ] )
    #~ env.AppendUnique( RPATH = [ ljsdk_path + '/target/usr/lib' ] )
    #~ env.AppendUnique( LIBPATH = [ ljsdk_path + '/target/usr/lib' ] )
    
    if_.linkflags += '-Wl,-rpath-link,' + ljapi_path + '/lib'
    if_.libpath += ljapi_path + '/lib'
    
    if_.linkflags += '-Wl,-rpath-link,' + ljsdk_path + '/target/lib'
    if_.libpath += ljsdk_path + '/target/lib'
    
    if_.linkflags += '-Wl,-rpath-link,' + ljsdk_path + '/target/usr/lib'
    if_.libpath += ljsdk_path + '/target/usr/lib'
    
    if_.libs += [ 'dl', 'ezxsort', 'drmfwudaclient', 'janus', 'm',
                  'dmnative', 'ezxjpegutils', 'ezxexif', 'ezxam',
                  'masauf', 'aplog', 'ezxsound', 'ezxappbase', 'pthread' ]
    
    
    
    _add_menu_parser_builder( env, ljsdk_path )

#//---------------------------------------------------------------------------//

def exists(env):
    return SCons.Tool.Tool( 'qt' ).exists( env )
