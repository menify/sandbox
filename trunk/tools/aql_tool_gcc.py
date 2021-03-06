
# Copyright (c) 2007, 2008 Konstantin Bozhikov
#
# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008 The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os
import subprocess
import SCons.Tool
import SCons.Util

import aql.utils
import aql.options
import aql.logging

_Error = aql.logging.Error
_PrependEnvPath = aql.utils.prependEnvPath
_EnvOptions = aql.options.EnvOptions

#//===========================================================================//

_cxx_suffixes = {'.cpp':1, '.cc':1, '.cxx':1, '.c++':1, '.C++':1, '.mm':1 }

if SCons.Util.case_sensitive_suffixes('.c', '.C'):
    _cxx_suffixes['.C'] = 1


#//===========================================================================//

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

def     _get_gcc_specs( env, options, gcc, check_existence_only, gcc_specs_cache = {} ):
    
    cc_ver, target = gcc_specs_cache.get( gcc, (None, None) )
    
    if cc_ver is None:
        
        os_env = os.environ.copy()
        _PrependEnvPath( os_env, 'PATH', env['ENV']['PATH'] )
        
        cc_ver = subprocess.Popen( gcc + ' -dumpversion', shell=True, stdout=subprocess.PIPE, env = os_env ).stdout.readline().strip()
        target = subprocess.Popen( gcc + ' -dumpmachine', shell=True, stdout=subprocess.PIPE, env = os_env ).stdout.readline().strip()
        
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
    
    def iscplusplus( source, _cxx_suffixes = _cxx_suffixes ):
        if source.suffix in _cxx_suffixes:
            return True
        
        for s in source.sources:
            if iscplusplus(s):
                return True
        
        return False
    
    def smart_link( source, target, env, for_signature ):
        for s in source:
            if iscplusplus( s ):
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

def     generate( env ):
    
    options = _EnvOptions(env)
    
    if not _try_gcc( env, options, check_existence_only = 0 ):
        _Error( "GCC has not been found (requested ver: %s, target: %s)" % (options.cc_ver, [str(options.target_os), str(options.target_machine) ] ) )
    
    #//-------------------------------------------------------//
    
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

