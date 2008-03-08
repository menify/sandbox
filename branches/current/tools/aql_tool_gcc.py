
import os
import os.path
import SCons.Tool

import aql.utils
import aql.options

_AppendEnvPath = aql.utils.appendEnvPath
_PrependEnvPath = aql.utils.prependEnvPath
_EnvOptions = aql.options.EnvOptions

def     _setup_flags( options ):
    
    if_ = options.If().cc_name['gcc']
    
    if_.target_os['windows'].user_interface['console'].linkflags += '-Wl,--subsystem,console'
    if_.target_os['windows'].user_interface['gui'].linkflags += '-Wl,--subsystem,windows'
    
    if_.debug_symbols['true'].ccflags += '-g'
    if_.debug_symbols['false'].linkflags += '-Wl,--strip-all'
    
    if_.link_runtime['static'].linkflags += '-Wl,-Bstatic'
    if_.link_runtime['shared'].linkflags += '-Wl,-Bdynamic'
    
    if_.target_os['windows'].runtime_threading['multi'].ccflags += '-mthreads'
    if_.target_os.ne('windows').runtime_threading['multi'].ccflags += '-pthreads'
    
    if_.optimization['speed'].occflags += '-O3 -ffast-math'
    if_.optimization['size'].occflags += '-Os -ffast-math'
    if_.optimization['off'].occflags += '-O0'
    
    if_.inlining['off'].occflags += '-fno-inline'
    if_.inlining['on'].occflags += '-finline -Wno-inline'
    if_.inlining['full'].occflags += '-finline-functions -Wno-inline'
    
    if_.rtti['true'].cxxflags += '-frtti'
    if_.rtti['false'].cxxflags += '-fno-rtti'
    
    if_.exception_handling['true'].cxxflags += '-fexceptions'
    if_.exception_handling['false'].cxxflags += '-fno-exceptions'
    
    if_.keep_asm['false'].ccflags += '-pipe'
    if_.keep_asm['true'].ccflags += '-fverbose-asm -save-temps'
    if_.keep_asm['true'].target_machine['x86'].ccflags -= '-masm=intel'
    
    
    if_.warning_level[0].ccflags += '-w'
    if_.warning_level[2].ccflags += '-Wall'
    if_.warning_level[3].ccflags += '-Wall'
    if_.warning_level[4].ccflags += '-Wall -Wextra'
    
    if_.warning_level[4].cc_ver.ge(4).ccflags += '-Wfatal-errors'
    
    if_.warnings_as_errors['on'].ccflags += '-Werror'
    
    if_.profiling['true'].ccflags += '-pg'
    if_.profiling['true'].linkflags += '-pg'

#//---------------------------------------------------------------------------//

def     _rpathlink( target, source, env, for_signature ):
    flags = ''
    for p in _EnvOptions(env).libpath.Get():
        flags += ' -Wl,-rpath-link,' + str(p)
    
    return flags

def     _setup_env_flags( env ):
    env['_AQL_GCC_RPATHLINK'] = _rpathlink
    env.Append( LINKFLAGS = ["$_AQL_GCC_RPATHLINK"] )

#//---------------------------------------------------------------------------//

def     _where_is_program( env, prog ):
    return env.WhereIs( prog ) or SCons.Util.WhereIs( prog )

#//---------------------------------------------------------------------------//

def     _find_gcc_tool( env, gcc_prefix, gcc_suffix, path, tool ):
    
    env_WhereIs = env.WhereIs
    
    return env_WhereIs( gcc_prefix + tool + gcc_suffix, path ) or \
           env_WhereIs( gcc_prefix + tool, path ) or \
           env_WhereIs( tool + gcc_suffix, path ) or \
           env_WhereIs( tool , path )

#//---------------------------------------------------------------------------//

def     _update_gcc_specs( env, options, gcc, check_existence_only ):
    
    os_environ = os.environ
    os_environ_path = os_environ['PATH']
    _AppendEnvPath( os_environ, 'PATH', env['ENV']['PATH'] )
    
    cc_ver = os.popen( gcc + ' -dumpversion', 'r').readline().strip()
    target = os.popen( gcc + ' -dumpmachine', 'r').readline().strip()
    
    os_environ['PATH'] = os_environ_path
    
    if target == 'mingw32':
        target_machine = 'i386'
        target_os = 'windows'
        target_cpu = target_machine
        target_os_release = ''
        target_os_version = ''
    
    else:
        target_list = target.split('-')
        
        target_list_len = len( target_list )
        if target_list_len == 2:
            target_machine = target_list[0]
            target_os = target_list[1]
        
        elif target_list_len > 2:
            target_machine = target_list[0]
            target_os = target_list[2]
        
        else:
            target_machine = ''
            target_os = ''
        
        target_cpu = target_machine
        target_os_release = ''
        target_os_version = ''
    
    if target_os.startswith('linux'):       target_os = 'linux'
    if target_machine.startswith('arm'):    target_machine = 'arm'
    
    if options.cc_ver.              isSetNotTo( cc_ver ):               return False
    if options.gcc_target.          isSetNotTo( target ):               return False
    if options.target_os.           isSetNotTo( target_os ):            return False
    if options.target_os_release.   isSetNotTo( target_os_release ):    return False
    if options.target_os_version.   isSetNotTo( target_os_version ):    return False
    if options.target_machine.      isSetNotTo( target_machine ):       return False
    if options.target_cpu.          isSetNotTo( target_cpu ):           return False
    
    if not check_existence_only:
        options.target_os = target_os
        options.target_os_release = target_os_release
        options.target_os_version = target_os_version
        options.target_machine = target_machine
        options.target_cpu = target_cpu
        
        options.cc_name = 'gcc'
        options.cc_ver = cc_ver
        options.gcc_target = target
    
    return True

#//---------------------------------------------------------------------------//

def     _try_gcc( env, options, check_existence_only ):
    
    if options.cc_name.isSetNotTo('gcc'):
        return None
    
    gcc_prefix = str(options.gcc_prefix)
    gcc_suffix = str(options.gcc_suffix)
    
    gcc = gcc_prefix + 'gcc' + gcc_suffix
    gxx = gcc_prefix + 'g++' + gcc_suffix
    
    gcc_path = _where_is_program( env, gcc )
    
    if gcc_path is None:
        return None
    
    gcc_path = os.path.normcase( gcc_path )
    
    if not _update_gcc_specs( env, options, gcc_path, check_existence_only ):
        return None
    
    path = os.path.dirname( gcc_path )
    
    gxx_path = env.WhereIs( gxx, path )
    if (gxx_path is None):
        return None
    
    gxx_path = os.path.normcase( gxx_path )
    
    as_path = _find_gcc_tool( env, gcc_prefix, gcc_suffix, path, 'as' )
    if (as_path is None):
        return None
    
    as_path = os.path.normcase( as_path )
    
    ar_path = _find_gcc_tool( env, gcc_prefix, gcc_suffix, path, 'ar' )
    if (ar_path is None):
        return None
    
    ar_path = os.path.normcase( ar_path )
    
    gcc_env = {}
    gcc_env['CC'] = gcc_path
    gcc_env['CXX'] = gxx_path
    gcc_env['AR'] = ar_path
    gcc_env['AS'] = as_path
    
    options.gcc_path = os.path.dirname( path )
    
    return gcc_env

#//---------------------------------------------------------------------------//

def     _update_os_env( env, options ):
    
    gcc_path = str(options.gcc_path)
    #~ gcc_target_platform = str(options.gcc_target)
    #~ gcc_ver = str(options.cc_ver)
    #~ gcc_suffix = str(options.gcc_suffix)
    
    _PrependEnvPath( env['ENV'], 'PATH', gcc_path )
    
    #~ cpppath_lib = options.cpppath_lib
    #~ cpppath_lib += gcc_path + '/include'
    #~ cpppath_lib += gcc_path + '/include/c++/' + gcc_ver
    #~ cpppath_lib += gcc_path + '/include/c++/' + gcc_ver + '/' + gcc_target_platform
    #~ cpppath_lib += gcc_path + '/lib/gcc/' + gcc_target_platform + '/' + gcc_ver + gcc_suffix + '/include'
    
    #~ options.libpath += gcc_path +'/lib'

#//---------------------------------------------------------------------------//

def     generate( env ):
    
    options = _EnvOptions(env)
    
    gcc_env = _try_gcc( env, options, check_existence_only = False )
    _update_os_env( env, options )
    
    
    # Some setting from the platform also have to be overridden
    env['OBJPREFIX']      = ''
    env['OBJSUFFIX']      = '.o'
    env['SHOBJPREFIX']    = '$OBJPREFIX'
    env['SHOBJSUFFIX']    = '$OBJSUFFIX'
    env['PROGPREFIX']     = ''
    env['PROGSUFFIX']     = ''
    env['LIBPREFIX']      = 'lib'
    env['LIBSUFFIX']      = '.a'
    env['SHLIBPREFIX']    = '$LIBPREFIX'
    env['SHLIBSUFFIX']    = '.so'
    env['LIBPREFIXES']    = [ '$LIBPREFIX' ]
    env['LIBSUFFIXES']    = [ '$LIBSUFFIX', '$SHLIBSUFFIX' ]
    
    _Tool = SCons.Tool.Tool
    for tool in ['cc', 'c++', 'link', 'ar', 'as']:
        _Tool( tool )( env )
    
    #//-------------------------------------------------------//
    
    env.Replace( **gcc_env )
    
    # target platform specific settings
    
    target_os = options.target_os
    
    if target_os == 'windows':
        _setup_env_windows( env )
    
    else:
        env['ARCOM']        = "${TEMPFILE('" + env['ARCOM']     + "')}"
        env['LINKCOM']      = "${TEMPFILE('" + env['LINKCOM']   + "')}"
        env['SHLINKCOM']    = "${TEMPFILE('" + env['SHLINKCOM'] + "')}"
        env['CXXCOM']       = "${TEMPFILE('" + env['CXXCOM']    + "')}"
        env['SHCXXCOM']     = "${TEMPFILE('" + env['SHCXXCOM']  + "')}"
        env['CCCOM']        = "${TEMPFILE('" + env['CCCOM']     + "')}"
        env['SHCCCOM']      = "${TEMPFILE('" + env['SHCCCOM']   + "')}"
    
        if target_os == 'cygwin':
            env['SHCCFLAGS'] = SCons.Util.CLVar('$CCFLAGS')
            env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS')
        else:
            env['SHCCFLAGS'] = SCons.Util.CLVar('$CCFLAGS -fPIC')
            env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS -fPIC')
        
            if target_os == 'sunos':
                env['SHOBJSUFFIX'] = '.pic.o'
            
            elif target_os == 'hpux':
                env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -shared -fPIC')
    
    # __RPATH is set to $_RPATH in the platform specification if that
    # platform supports it.
    env.Append(LINKFLAGS=['$__RPATH'])
    env['RPATHPREFIX'] = '-Wl,-rpath='
    env['RPATHSUFFIX'] = ''
    env['_RPATH'] = '${_concat(RPATHPREFIX, RPATH, RPATHSUFFIX, __env__)}'
    
    _setup_flags( options )
    _setup_env_flags( env )
    

#//---------------------------------------------------------------------------//

def exists( env ):
    return _try_gcc( env, _EnvOptions(env), check_existence_only = True ) is not None


#//===========================================================================//
#  Setting up windows environment
#//===========================================================================//

_shlib_action = None
_res_builder = None

def     _setup_windows_globals():
    
    global _shlib_action
    global _res_builder

    if _shlib_action is not None:
        return
    
    _shlib_action    = SCons.Action.Action( shlib_generator, generator=1 )
    res_action      = SCons.Action.Action('$RCCOM', '$RCCOMSTR' )
    _res_builder     = SCons.Builder.Builder( action=res_action, suffix='.o',
                                             source_scanner=SCons.Tool.SourceFileScanner )
    
    SCons.Tool.SourceFileScanner.add_scanner( '.rc', SCons.Defaults.CScan )

#//-------------------------------------------------------//

def     _setup_env_windows( env ):
    
    _setup_windows_globals()
    
    env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS')
    env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -shared')
    
    env['SHLINKCOM']   = _shlib_action
    
    env.Append(SHLIBEMITTER = [shlib_emitter])
    
    env['WIN32DEFPREFIX']        = ''
    env['WIN32DEFSUFFIX']        = '.def'
    env['WINDOWSDEFPREFIX']      = '${WIN32DEFPREFIX}'
    env['WINDOWSDEFSUFFIX']      = '${WIN32DEFSUFFIX}'
    
    env['SHOBJSUFFIX'] = '.o'
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1

    env['RC'] = 'windres'
    env['RCFLAGS'] = SCons.Util.CLVar('')
    env['RCINCFLAGS'] = '$( ${_concat(RCINCPREFIX, CPPPATH, RCINCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)'
    env['RCINCPREFIX'] = '--include-dir '
    env['RCINCSUFFIX'] = ''
    env['RCCOM'] = '$RC $_CPPDEFFLAGS $RCINCFLAGS ${RCINCPREFIX} ${SOURCE.dir} $RCFLAGS -i $SOURCE -o $TARGET'
    env['BUILDERS']['RES'] = _res_builder

#//-------------------------------------------------------//

def shlib_generator(target, source, env, for_signature):
    cmd = SCons.Util.CLVar(['$SHLINK', '$SHLINKFLAGS']) 
    
    dll = env.FindIxes(target, 'SHLIBPREFIX', 'SHLIBSUFFIX')
    if dll: cmd.extend(['-o', dll])
    
    cmd.extend(['$SOURCES', '$_LIBDIRFLAGS', '$_LIBFLAGS'])
    
    implib = env.FindIxes(target, 'LIBPREFIX', 'LIBSUFFIX')
    if implib: cmd.append('-Wl,--out-implib,'+implib.get_string(for_signature))
    
    def_target = env.FindIxes(target, 'WINDOWSDEFPREFIX', 'WINDOWSDEFSUFFIX')
    if def_target: cmd.append('-Wl,--output-def,'+def_target.get_string(for_signature))
    
    return [cmd]

#//-------------------------------------------------------//

def shlib_emitter(target, source, env):
    dll = env.FindIxes(target, 'SHLIBPREFIX', 'SHLIBSUFFIX')
    no_import_lib = env.get('no_import_lib', 0)
    
    if not dll:
        raise SCons.Errors.UserError, "A shared library should have exactly one target with the suffix: %s" % env.subst("$SHLIBSUFFIX")
    
    if not no_import_lib and \
       not env.FindIxes(target, 'LIBPREFIX', 'LIBSUFFIX'):
        
        # Append an import library to the list of targets.
        target.append(env.ReplaceIxes(dll,  
                                      'SHLIBPREFIX', 'SHLIBSUFFIX',
                                      'LIBPREFIX', 'LIBSUFFIX'))

    # Append a def file target if there isn't already a def file target
    # or a def file source. There is no option to disable def file
    # target emitting, because I can't figure out why someone would ever
    # want to turn it off.
    def_source = env.FindIxes(source, 'WINDOWSDEFPREFIX', 'WINDOWSDEFSUFFIX')
    def_target = env.FindIxes(target, 'WINDOWSDEFPREFIX', 'WINDOWSDEFSUFFIX')
    if not def_source and not def_target:
        target.append(env.ReplaceIxes(dll,  
                                      'SHLIBPREFIX', 'SHLIBSUFFIX',
                                      'WINDOWSDEFPREFIX', 'WINDOWSDEFSUFFIX'))
    
    return (target, source)

