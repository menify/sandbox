
import os
import os.path
import SCons.Tool

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
    
    if_.optimization['speed'].ccflags += '-O3 -ffast-math'
    if_.optimization['size'].ccflags += '-Os -ffast-math'
    if_.optimization['off'].ccflags += '-O0'
    
    if_.inlining['off'].ccflags += '-fno-inline'
    if_.inlining['on'].ccflags += '-finline -Wno-inline'
    if_.inlining['full'].ccflags += '-finline-functions -Wno-inline'
    
    if_.rtti['true'].ccflags += '-frtti'
    if_.rtti['false'].ccflags += '-fno-rtti'
    
    if_.exception_handling['true'].ccflags += '-fexceptions'
    if_.exception_handling['false'].ccflags += '-fno-exceptions'
    
    if_.keep_asm['true'].ccflags += '-masm=intel -fverbose-asm -save-temps'
    
    if_.warning_level[0].ccflags += '-w'
    if_.warning_level[2].ccflags += '-Wall'
    if_.warning_level[3].ccflags += '-Wall'
    if_.warning_level[4].ccflags += '-Wall -Wextra'
    
    if_.warning_level[4].cc_ver.ge(4).ccflags += '-Wfatal-errors'
    
    if_.warnings_as_errors['on'].ccflags += '-Werror'

#//---------------------------------------------------------------------------//

def     _find_gcc_tool( env, gcc_prefix, gcc_suffix, path, tool ):
    
    env_WhereIs = env.WhereIs
    
    return env_WhereIs( gcc_prefix + tool + gcc_suffix, path ) or \
           env_WhereIs( gcc_prefix + tool, path ) or \
           env_WhereIs( tool + gcc_suffix, path ) or \
           env_WhereIs( tool , path )

#//---------------------------------------------------------------------------//

def     _find_gcc( env, options ):
    
    if (options.cc_name != '') and (options.cc_name != 'gcc'):
        return None
    
    gcc_prefix = str(options.gcc_prefix)
    gcc_suffix = str(options.gcc_suffix)
    
    gcc = gcc_prefix + 'gcc' + gcc_suffix
    gxx = gcc_prefix + 'g++' + gcc_suffix
    
    gcc_path = env.WhereIs( gcc )
    if gcc_path is None:
        return None
    
    gcc_path = os.path.normcase( gcc_path )
    
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
    
    return (gcc_env, path)

#//---------------------------------------------------------------------------//

def     _get_gcc_specs( options, gcc ):
    
    options.cc_name = 'gcc'
    options.cc_ver = os.popen( gcc + ' -dumpversion', 'r').readline().strip()
    target = os.popen( gcc + ' -dumpmachine', 'r').readline().strip()
    
    if target == 'mingw32':
        target_machine = 'i386'
        target_cpu = ''
        target_os = 'windows'
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
            
        target_cpu = ''
        target_os_release = ''
        target_os_version = ''
    
    if not options.target_os.IsChanged():
        options.target_os = target_os
        options.target_os_release = target_os_release
        options.target_os_version = target_os_version
    
    if not options.target_machine.IsChanged():
        options.target_machine = target_machine
        options.target_cpu = target_cpu

#//---------------------------------------------------------------------------//

def     generate( env ):
    
    options = env['AQL_OPTIONS']
    
    gcc_env, path = _find_gcc( env, options )
    
    _get_gcc_specs( options, gcc_env['CC'] )
    
    env.PrependENVPath('PATH', path )
        
    _Tool = SCons.Tool.Tool
    for tool in ['cc', 'c++', 'link', 'ar', 'as']:
        _Tool( tool )( env )
    
    #//-------------------------------------------------------//
    
    env.Replace( **gcc_env )
    
    target_os = str(options.target_os)
    
    if target_os == 'windows':
        _setup_env_windows( env )
    
    elif target_os == 'cygwin':
        env['SHCCFLAGS'] = SCons.Util.CLVar('$CCFLAGS')
        env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS')
    else:
        env['SHCCFLAGS'] = SCons.Util.CLVar('$CCFLAGS -fPIC')
        env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS -fPIC')
    
        if target_os == 'sunos':
            env['SHOBJSUFFIX'] = '.pic.o'
        
        if target_os == 'hpux':
            env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -shared -fPIC')
        
        env['PROGSUFFIX'] = ''
        env['SHLIBSUFFIX'] = '.so'
    
    # __RPATH is set to $_RPATH in the platform specification if that
    # platform supports it.
    env.Append(LINKFLAGS=['$__RPATH'])
    env['RPATHPREFIX'] = '-Wl,-rpath='
    env['RPATHSUFFIX'] = ''
    env['_RPATH'] = '${_concat(RPATHPREFIX, RPATH, RPATHSUFFIX, __env__)}'
    
    _setup_flags( options )
    
#//---------------------------------------------------------------------------//

def exists( env ):
    return _find_gcc( env, env['AQL_OPTIONS'] ) is not None


#//===========================================================================//
#  Setting up windows environment
#//===========================================================================//

_windows_globals_is_set = 0
_shlib_action = None
_res_builder = None

def     _setup_windows_globals():
    
    global _windows_globals_is_set
    if _windows_globals_is_set:
        return
    
    _windows_globals_is_set = 1
    
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
    
    # Some setting from the platform also have to be overridden:
    env['OBJSUFFIX'] = '.o'
    env['LIBPREFIX'] = 'lib'
    env['LIBSUFFIX'] = '.a'

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

