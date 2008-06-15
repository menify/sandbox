
import os
import SCons.Tool
import SCons.Util

import aql.utils
import aql.options

_AppendEnvPath = aql.utils.appendEnvPath
_PrependEnvPath = aql.utils.prependEnvPath
_EnvOptions = aql.options.EnvOptions

#//===========================================================================//

_cxx_suffixes = {'.cpp':1, '.cc':1, '.cxx':1, '.c++':1, '.C++':1, '.mm':1 }

if SCons.Util.case_sensitive_suffixes('.c', '.C'):
    _cxx_suffixes['.C'] = 1


#//===========================================================================//

def     _setup_flags( options ):
    
    if_ = options.If()
    
    if_.target_os['windows'].user_interface['console'].linkflags += '-Wl,--subsystem,console'
    if_.target_os['windows'].user_interface['gui'].linkflags += '-Wl,--subsystem,windows'
    
    if_.debug_symbols['true'].ccflags += '-g'
    if_.debug_symbols['false'].linkflags += '-Wl,--strip-all'
    
    if_.link_runtime['static'].linkflags += '-static-libgcc'
    if_.link_runtime['shared'].linkflags += '-shared-libgcc'
    
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
    if_.keep_asm['true'].target_machine['x86'].ccflags += '-masm=intel'
    
    
    if_.warning_level[0].ccflags += '-w'
    if_.warning_level[2].ccflags += '-Wall'
    if_.warning_level[3].ccflags += '-Wall'
    if_.warning_level[4].ccflags += '-Wall -Wextra'
    
    if_.warning_level[4].cc_ver.ge(4).ccflags += '-Wfatal-errors'
    
    if_.warnings_as_errors['on'].ccflags += '-Werror'
    
    if_profiling_true = if_.profiling['true']
    if_profiling_true.ccflags += '-pg'
    if_profiling_true.linkflags += '-pg'
    if_profiling_true.linkflags -= '-Wl,--strip-all'

#//---------------------------------------------------------------------------//

def     _add_libs( env ):
    env['_LIBFLAGS'] = '--start-group ' + env['_LIBFLAGS'] + ' --end-group'
    #~ env.Append( LIBS = ["$_AQL_LIBS"] )       # duplicate libs to resolve recursive dependencies

def     _rpathlink( target, source, env, for_signature ):
    flags = ''
    for p in _EnvOptions(env).libpath.Value():
        flags += ' -Wl,-rpath-link,' + str(p)
    
    return flags

def     _add_rpath( env ):
    
    # __RPATH is set to $_RPATH in the platform specification if that
    # platform supports it.
    
    env['_AQL_GCC_RPATHLINK'] = _rpathlink
    env.Append( LINKFLAGS = ["$_AQL_GCC_RPATHLINK"] )
    
    env.Append( LINKFLAGS=['$__RPATH'] )
    env['RPATHPREFIX'] = '-Wl,-rpath='
    env['RPATHSUFFIX'] = ''
    env['_RPATH'] = '${_concat(RPATHPREFIX, RPATH, RPATHSUFFIX, __env__)}'


#//---------------------------------------------------------------------------//

def     _where_is_program( env, prog, normcase = os.path.normcase ):
    tool_path =  env.WhereIs( prog ) or SCons.Util.WhereIs( prog )
    
    if tool_path:
        return normcase( tool_path )
    
    print prog,": ", tool_path
    
    return tool_path


#//---------------------------------------------------------------------------//

def     _find_gcc_tool( env, gcc_prefix, gcc_suffix, path, tool,
                        normcase = os.path.normcase ):
    
    env_WhereIs = env.WhereIs
    
    tool_path = env_WhereIs( gcc_prefix + tool + gcc_suffix, path ) or \
                env_WhereIs( gcc_prefix + tool, path ) or \
                env_WhereIs( tool + gcc_suffix, path ) or \
                env_WhereIs( tool , path )
    
    if tool_path:
        return normcase( tool_path )
    
    return tool_path

#//---------------------------------------------------------------------------//

if not aql.utils.__dict__.has_key( 'gcc_specs_cache' ):
    aql.utils.gcc_specs_cache = {}

def     _get_gcc_specs( env, options, gcc, check_existence_only, gcc_specs_cache = aql.utils.gcc_specs_cache ):
    
    cc_ver, target = gcc_specs_cache.get( gcc, (None, None) )
    
    if cc_ver is None:
        os_environ = os.environ
        os_environ_path = os_environ['PATH']
        _AppendEnvPath( os_environ, 'PATH', env['ENV']['PATH'] )
        
        cc_ver = os.popen( gcc + ' -dumpversion', 'r').readline().strip()
        target = os.popen( gcc + ' -dumpmachine', 'r').readline().strip()
        
        os_environ['PATH'] = os_environ_path
        gcc_specs_cache[ gcc ] = ( cc_ver, target )
    
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
    
    if target_os == 'mingw32':              target_os = 'windows'
    if target_os.startswith('linux'):       target_os = 'linux'
    if target_machine.startswith('arm'):    target_machine = 'arm'
    
    
    if options.cc_ver               != cc_ver or \
       options.gcc_target           != target or \
       options.target_os            != target_os or \
       options.target_os_release    != target_os_release or \
       options.target_os_version    != target_os_version or \
       options.target_machine       != target_machine or \
       options.target_cpu           != target_cpu:
       
       return 0
    
    if not check_existence_only:
        options.target_os = target_os
        options.target_os_release = target_os_release
        options.target_os_version = target_os_version
        options.target_machine = target_machine
        options.target_cpu = target_cpu
        
        options.cc_name = 'gcc'
        options.cc_ver = cc_ver
        options.gcc_target = target
    
    return 1

#//---------------------------------------------------------------------------//

def     _try_gcc( env, options, check_existence_only ):
    
    if options.cc_name != 'gcc':
        return 0
    
    gcc_prefix = str(options.gcc_prefix)
    gcc_suffix = str(options.gcc_suffix)
    
    gcc = gcc_prefix + 'gcc' + gcc_suffix
    gxx = gcc_prefix + 'g++' + gcc_suffix
    
    gcc_path = _where_is_program( env, gcc )
    
    if not gcc_path:
        return 0
        
    if not _get_gcc_specs( env, options, gcc_path, check_existence_only ):
        return 0
    
    path = os.path.dirname( gcc_path )
    
    if not check_existence_only:
        _add_gcc( env, gcc_path )
        _add_link( env )
    
    for t,f in ( ('g++', _add_gxx), ('ar', _add_ar), ('ranlib', _add_ranlib), ('as', _add_as) ):
        tool_path = _find_gcc_tool( env, gcc_prefix, gcc_suffix, path, t )
        
        if tool_path is None:
            if t == 'ranlib':
                continue
            
            return 0
        
        if not check_existence_only:
            f( env, tool_path )
    
    if not check_existence_only:
        options.gcc_path = os.path.dirname( path )
    
    return 1

#//===========================================================================//

def     _add_gcc( env, gcc_path ):
    
    CSuffixes = ['.c', '.m']
    if not SCons.Util.case_sensitive_suffixes('.c', '.C'):
        CSuffixes.append('.C')
    
    """
    Add Builders and construction variables for C compilers to an Environment.
    """
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)
    
    for suffix in CSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCAction)
        static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)
        shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)
    
    env['_CCCOMCOM'] = '$CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS'
    env['CCFLAGS'] = SCons.Util.CLVar('')
    env['SHCCFLAGS'] = SCons.Util.CLVar('$CCFLAGS -fPIC')
    env['FRAMEWORKS'] = SCons.Util.CLVar('')
    env['FRAMEWORKPATH'] = SCons.Util.CLVar('')
    
    if env['PLATFORM'] == 'darwin':
        env['_CCCOMCOM'] = env['_CCCOMCOM'] + ' $_FRAMEWORKPATH'
    
    env['CC']        = gcc_path
    env['CFLAGS']    = SCons.Util.CLVar('')
    env['CCCOM']     = '$CC -o $TARGET -c $CFLAGS $CCFLAGS $_CCCOMCOM $SOURCES'
    env['SHCC']      = '$CC'
    env['SHCFLAGS'] = SCons.Util.CLVar('$CFLAGS')
    env['SHCCCOM']   = '$SHCC -o $TARGET -c $SHCFLAGS $SHCCFLAGS $_CCCOMCOM $SOURCES'
    
    env['CPPDEFPREFIX']  = '-D'
    env['CPPDEFSUFFIX']  = ''
    env['INCPREFIX']  = '-I'
    env['INCSUFFIX']  = ''
    
    env['OBJPREFIX']      = ''
    env['OBJSUFFIX']      = '.o'
    env['SHOBJPREFIX']    = '${OBJPREFIX}'
    env['SHOBJSUFFIX']    = '.os'
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 0
    
    env['CFILESUFFIX'] = '.c'

#//===========================================================================//

def     _add_gxx( env, gxx_path ):
    
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)
    
    for suffix in _cxx_suffixes.iterkeys():
        static_obj.add_action(suffix, SCons.Defaults.CXXAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCXXAction)
        static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)
        shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)
    
    env['CXX']        = gxx_path
    env['CXXFLAGS']   = SCons.Util.CLVar('')
    env['CXXCOM']     = '$CXX -o $TARGET -c $CXXFLAGS $CCFLAGS $_CCCOMCOM $SOURCES'
    env['SHCXX']      = '$CXX'
    env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS')
    env['SHCXXCOM']   = '$SHCXX -o $TARGET -c $SHCXXFLAGS $SHCCFLAGS $_CCCOMCOM $SOURCES'
    
    env['CXXFILESUFFIX'] = '.cc'


#//===========================================================================//

def     _add_link( env ):
    
    def smart_link( source, target, env, for_signature,
                    toSequence = aql.utils.toSequence,
                    splitext = os.path.splitext,
                    _cxx_suffixes = _cxx_suffixes ):
        
        for s in toSequence( source ):
            if s.sources:
                ext = splitext( str(s.sources[0]) )[1]
                if _cxx_suffixes.has_key( ext ):
                    return '$CXX'
        
        return '$CC'
    
    #//-------------------------------------------------------//
    
    def shlib_emitter(target, source, env):
        for tgt in target:
            tgt.attributes.shared = 1
        return (target, source)
    
    #//-------------------------------------------------------//
    
    """Add Builders and construction variables for gnulink to an Environment."""
    SCons.Tool.createSharedLibBuilder(env)
    SCons.Tool.createProgBuilder(env)

    env['SHLINK']      = '$LINK'
    env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -shared')
    env['SHLINKCOM']   = '$SHLINK -o $TARGET $SHLINKFLAGS $SOURCES $_LIBDIRFLAGS $_LIBFLAGS'
    # don't set up the emitter, cause AppendUnique will generate a list
    # starting with None :-(
    env.Append(SHLIBEMITTER = [shlib_emitter])
    env['SMARTLINK']   = smart_link
    env['LINK']        = "$SMARTLINK"
    env['LINKFLAGS']   = SCons.Util.CLVar('')
    env['LINKCOM']     = '$LINK -o $TARGET $LINKFLAGS $SOURCES $_LIBDIRFLAGS $_LIBFLAGS'
    env['LIBDIRPREFIX']='-L'
    env['LIBDIRSUFFIX']=''
    
    env['LIBPREFIXES']    = [ '$LIBPREFIX' ]
    env['LIBSUFFIXES']    = [ '$LIBSUFFIX', '$SHLIBSUFFIX' ]
    env['_LIBFLAGS']='${_stripixes(LIBLINKPREFIX, LIBS, LIBLINKSUFFIX, LIBPREFIXES, LIBSUFFIXES, __env__)}'
    env['LIBLINKPREFIX']='-l'
    env['LIBLINKSUFFIX']=''
    
    env['PROGPREFIX']     = ''
    env['PROGSUFFIX']     = ''
    
    env['SHLIBPREFIX']    = '${LIBPREFIX}'
    env['SHLIBSUFFIX']    = '.so'
    
    if env['PLATFORM'] == 'hpux':
        env['SHLIBSUFFIX'] = '.sl'
    elif env['PLATFORM'] == 'aix':
        env['SHLIBSUFFIX'] = '.a'

    # For most platforms, a loadable module is the same as a shared
    # library.  Platforms which are different can override these, but
    # setting them the same means that LoadableModule works everywhere.
    SCons.Tool.createLoadableModuleBuilder(env)
    env['LDMODULE'] = '$SHLINK'
    env['LDMODULEPREFIX'] = '${SHLIBPREFIX}'
    env['LDMODULESUFFIX'] = '${SHLIBSUFFIX}'
    env['LDMODULEFLAGS'] = '$SHLINKFLAGS'
    env['LDMODULECOM'] = '$SHLINKCOM'

#//===========================================================================//

def     _add_ar( env, ar_path ):
    
    SCons.Tool.createStaticLibBuilder(env)

    env['AR']          = ar_path
    env['ARFLAGS']     = SCons.Util.CLVar('rc')
    env['ARCOM']       = '$AR $ARFLAGS $TARGET $SOURCES'
    env['LIBPREFIX']   = 'lib'
    env['LIBSUFFIX']   = '.a'

#//===========================================================================//

def     _add_ranlib( env, ranlib_path ):
    env['RANLIB']      = ranlib_path
    env['RANLIBFLAGS'] = SCons.Util.CLVar('')
    env['RANLIBCOM']   = '$RANLIB $RANLIBFLAGS $TARGET'

#//===========================================================================//

def     _add_as( env, as_path ):
    
    as_suffixes = [ '.s' ]
    as_pp_suffixes = ['.spp', '.SPP']
    
    if SCons.Util.case_sensitive_suffixes('.s', '.S'):
        as_pp_suffixes.append('.S')
    else:
        as_suffixes.append('.S')
    
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)
    
    for suffix in as_suffixes:
        static_obj.add_action(suffix, SCons.Defaults.ASAction)
        shared_obj.add_action(suffix, SCons.Defaults.ASAction)
        static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)
        shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)

    for suffix in as_pp_suffixes:
        static_obj.add_action(suffix, SCons.Defaults.ASPPAction)
        shared_obj.add_action(suffix, SCons.Defaults.ASPPAction)
        static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)
        shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)

    env['AS']        = as_path
    env['ASFLAGS']   = SCons.Util.CLVar('')
    env['ASCOM']     = '$AS $ASFLAGS -o $TARGET $SOURCES'
    env['ASPPFLAGS'] = '$ASFLAGS'
    env['ASPPCOM']   = '$CC $ASPPFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS -c -o $TARGET $SOURCES'

#//---------------------------------------------------------------------------//

def     _add_stdlib_paths( options ):
    
    gcc_path = str(options.gcc_path)
    gcc_target_platform = str(options.gcc_target)
    gcc_ver = str(options.cc_ver)
    gcc_suffix = str(options.gcc_suffix)
    
    gcc_cpppath_cc = gcc_path + '/include'
    gcc_cpppath_cxx = gcc_cpppath_cc + '/c++'
    
    gcc_lib_cpppath_cc = gcc_path + '/lib/gcc/' + gcc_target_platform + '/' + gcc_ver + gcc_suffix + '/include'
    gcc_lib_cpppath_cxx = gcc_lib_cpppath_cc + '/c++'
    
    gcc_cpppath = \
        [
            gcc_lib_cpppath_cxx + '/' + gcc_target_platform,
            gcc_lib_cpppath_cxx,
            gcc_lib_cpppath_cc,
            
            gcc_cpppath_cxx + '/' + gcc_ver + '/' + gcc_target_platform,
            gcc_cpppath_cxx + '/' + gcc_ver,
            gcc_cpppath_cxx,
            gcc_cpppath_cc
        ]
    
    options.cpppath_lib += gcc_cpppath
    options.libpath += gcc_path +'/lib'

#//---------------------------------------------------------------------------//

def     generate( env ):
    
    options = _EnvOptions(env)
    
    if not _try_gcc( env, options, check_existence_only = 0 ):
        return
    
    #//-------------------------------------------------------//
    
    _add_stdlib_paths( options )
    
    # target platform specific settings
    
    target_os = options.target_os
    
    if target_os == 'windows':
        _setup_env_windows( env )
    
    else:
        if target_os == 'cygwin':
            env['SHCCFLAGS'] = SCons.Util.CLVar('$CCFLAGS')
            env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS')
            
            env['SHOBJSUFFIX'] = '$OBJSUFFIX'
            env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1
            
            env['PROGSUFFIX']  = '.exe'
            env['SHLIBSUFFIX'] = '.dll'
        
        else:
            if target_os == 'sunos':
                env['SHOBJSUFFIX'] = '.pic.o'
            
            elif target_os == 'hpux':
                env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -shared -fPIC')
         
            # This platform supports RPATH specifications
            env['__RPATH'] = '$_RPATH'
    
    _add_rpath( env )
    _add_libs( env )
    
    env['ARCOM']        = "${TEMPFILE('" + env['ARCOM']     + "')}"
    env['LINKCOM']      = "${TEMPFILE('" + env['LINKCOM']   + "')}"
    
    if target_os != 'windows':
        env['SHLINKCOM']    = "${TEMPFILE('" + env['SHLINKCOM'] + "')}"
    
    env['CXXCOM']       = "${TEMPFILE('" + env['CXXCOM']    + "')}"
    env['SHCXXCOM']     = "${TEMPFILE('" + env['SHCXXCOM']  + "')}"
    env['CCCOM']        = "${TEMPFILE('" + env['CCCOM']     + "')}"
    env['SHCCCOM']      = "${TEMPFILE('" + env['SHCCCOM']   + "')}"
    
    _setup_flags( options )


#//---------------------------------------------------------------------------//

def exists( env ):
    return _try_gcc( env, _EnvOptions(env), check_existence_only = 1 )


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
    
    env['PROGSUFFIX']     = '.exe'
    env['SHLIBSUFFIX']    = '.dll'
    
    env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS')
    env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS -shared')
    
    env['SHLINKCOM']   = _shlib_action
    
    env.Append(SHLIBEMITTER = [shlib_emitter])
    
    env['WIN32DEFPREFIX']        = '${SHLIBPREFIX}'
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

