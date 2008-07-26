
# Copyright (c) 2008 Konstantin Bozhikov
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

import re
import os.path
import subprocess

import SCons.Action
import SCons.Defaults
import SCons.Errors
import SCons.Platform.win32
import SCons.Tool
import SCons.Util

import aql.utils
import aql.options
import aql.logging

_EnvOptions = aql.options.EnvOptions
_PrependEnvPath = aql.utils.prependEnvPath
_Info = aql.logging.Info

#//---------------------------------------------------------------------------//

def     _setup_flags( options ):
    
    if_ = options.If()
    
    if_.debug_symbols['true'].ccflags += '/Z7'
    if_.debug_symbols['true'].linkflags += '/DEBUG'
    
    if_.user_interface['console'].linkflags += '/subsystem:console'
    if_.user_interface['gui'].linkflags += '/subsystem:windows'
    
    if_.link_runtime['shared'].runtime_debugging['false'].ccflags += '/MD'
    if_.link_runtime['shared'].runtime_debugging['true'].ccflags += '/MDd'
    if_.link_runtime['static'].runtime_debugging['false'].runtime_threading['single'].ccflags += '/ML'
    if_.link_runtime['static'].runtime_debugging['false'].runtime_threading['multi'].ccflags += '/MT'
    if_.link_runtime['static'].runtime_debugging['true'].runtime_threading['single'].ccflags += '/MLd'
    if_.link_runtime['static'].runtime_debugging['true'].runtime_threading['multi'].ccflags += '/MTd'
    
    if_.cc_ver.ge(7).cc_ver.lt(8).ccflags += '/Zc:forScope /Zc:wchar_t'
    
    if_.optimization['speed'].cc_ver.ge(8).occflags += '/O2'
    if_.optimization['speed'].cc_ver.lt(8).occflags += '/Ogity /O2 /Gr /GF /Gy'
    if_.optimization['speed'].olinkflags += '/OPT:REF /OPT:ICF'
    
    if_.optimization['size'].cc_ver.ge(8).occflags += '/O1'
    if_.optimization['size'].cc_ver.lt(8).occflags += '/Ogisy /O1 /Gr /GF /Gy'
    if_.optimization['size'].olinkflags += '/OPT:REF /OPT:ICF'
    
    if_.optimization['off'].occflags += '/Od'
    
    if_.inlining['off'].occflags += '/Ob0'
    if_.inlining['on'].occflags += '/Ob1'
    if_.inlining['full'].occflags += '/Ob2'
    
    if_.rtti['true'].cxxflags += '/GR'
    if_.rtti['false'].cxxflags += '/GR-'
    
    if_.exception_handling['true'].cxxflags += '/EHsc'
    if_.exception_handling['false'].cxxflags += '/EHs- /EHc-'
    
    if_.keep_asm['true'].ccflags += '/Fa${TARGET.base}.asm /FAs'
    
    if_.warning_level[0].ccflags += '/w'
    if_.warning_level[1].ccflags += '/W1'
    if_.warning_level[2].ccflags += '/W2'
    if_.warning_level[3].ccflags += '/W3'
    if_.warning_level[4].ccflags += '/W4'
    
    if_.warnings_as_errors['on'].ccflags += '/WX'
    
    if_.linkflags += '/INCREMENTAL:NO'


#//---------------------------------------------------------------------------//

def validate_vars(env):
    """Validate the PCH and PCHSTOP construction variables."""
    if env.has_key('PCH') and env['PCH']:
        if not env.has_key('PCHSTOP'):
            raise SCons.Errors.UserError, "The PCHSTOP construction must be defined if PCH is defined."
        if not SCons.Util.is_String(env['PCHSTOP']):
            raise SCons.Errors.UserError, "The PCHSTOP construction variable must be a string: %r"%env['PCHSTOP']

def pch_emitter(target, source, env):
    """Adds the object file target."""

    validate_vars(env)

    pch = None
    obj = None

    for t in target:
        if SCons.Util.splitext(str(t))[1] == '.pch':
            pch = t
        if SCons.Util.splitext(str(t))[1] == '.obj':
            obj = t

    if not obj:
        obj = SCons.Util.splitext(str(pch))[0]+'.obj'

    target = [pch, obj] # pch must be first, and obj second for the PCHCOM to work

    return (target, source)

def object_emitter(target, source, env, parent_emitter):
    """Sets up the PCH dependencies for an object file."""

    validate_vars(env)

    parent_emitter(target, source, env)

    if env.has_key('PCH') and env['PCH']:
        env.Depends(target, env['PCH'])

    return (target, source)

def static_object_emitter(target, source, env):
    return object_emitter(target, source, env,
                          SCons.Defaults.StaticObjectEmitter)

def shared_object_emitter(target, source, env):
    return object_emitter(target, source, env,
                          SCons.Defaults.SharedObjectEmitter)

pch_action = SCons.Action.Action('$PCHCOM', '$PCHCOMSTR')
pch_builder = SCons.Builder.Builder(action=pch_action, suffix='.pch',
                                    emitter=pch_emitter,
                                    source_scanner=SCons.Tool.SourceFileScanner)
res_action = SCons.Action.Action('$RCCOM', '$RCCOMSTR')
res_builder = SCons.Builder.Builder(action=res_action,
                                    src_suffix='.rc',
                                    suffix='.res',
                                    src_builder=[],
                                    source_scanner=SCons.Tool.SourceFileScanner)

SCons.Tool.SourceFileScanner.add_scanner('.rc', SCons.Defaults.CScan)

#//---------------------------------------------------------------------------//

def pdbGenerator(env, target, source, for_signature):
    try:
        return ['/PDB:%s' % target[0].attributes.pdb, '/DEBUG']
    except (AttributeError, IndexError):
        return None

def windowsShlinkTargets(target, source, env, for_signature):
    listCmd = []
    dll = env.FindIxes(target, 'SHLIBPREFIX', 'SHLIBSUFFIX')
    if dll: listCmd.append("/out:%s"%dll.get_string(for_signature))

    implib = env.FindIxes(target, 'LIBPREFIX', 'LIBSUFFIX')
    if implib: listCmd.append("/implib:%s"%implib.get_string(for_signature))

    return listCmd

def windowsShlinkSources(target, source, env, for_signature):
    listCmd = []

    deffile = env.FindIxes(source, "WINDOWSDEFPREFIX", "WINDOWSDEFSUFFIX")
    for src in source:
        if src == deffile:
            # Treat this source as a .def file.
            listCmd.append("/def:%s" % src.get_string(for_signature))
        else:
            # Just treat it as a generic source file.
            listCmd.append(src)
    return listCmd

def windowsLibEmitter(target, source, env):
    validate_vars(env)

    extratargets = []
    extrasources = []

    dll = env.FindIxes(target, "SHLIBPREFIX", "SHLIBSUFFIX")
    no_import_lib = env.get('no_import_lib', 0)

    if not dll:
        raise SCons.Errors.UserError, "A shared library should have exactly one target with the suffix: %s" % env.subst("$SHLIBSUFFIX")

    insert_def = env.subst("$WINDOWS_INSERT_DEF")
    if not insert_def in ['', '0', 0] and \
       not env.FindIxes(source, "WINDOWSDEFPREFIX", "WINDOWSDEFSUFFIX"):

        # append a def file to the list of sources
        extrasources.append(
            env.ReplaceIxes(dll,
                            "SHLIBPREFIX", "SHLIBSUFFIX",
                            "WINDOWSDEFPREFIX", "WINDOWSDEFSUFFIX"))

    version_num, suite = SCons.Tool.msvs.msvs_parse_version(env.get('MSVS_VERSION', '6.0'))
    if version_num >= 8.0 and env.get('WINDOWS_INSERT_MANIFEST', 0):
        # MSVC 8 automatically generates .manifest files that must be installed
        extratargets.append(
            env.ReplaceIxes(dll,
                            "SHLIBPREFIX", "SHLIBSUFFIX",
                            "WINDOWSSHLIBMANIFESTPREFIX", "WINDOWSSHLIBMANIFESTSUFFIX"))

    if env.has_key('PDB') and env['PDB']:
        pdb = env.arg2nodes('$PDB', target=target, source=source)[0]
        extratargets.append(pdb)
        target[0].attributes.pdb = pdb

    if not no_import_lib and \
       not env.FindIxes(target, "LIBPREFIX", "LIBSUFFIX"):
        # Append an import library to the list of targets.
        extratargets.append(
            env.ReplaceIxes(dll,
                            "SHLIBPREFIX", "SHLIBSUFFIX",
                            "LIBPREFIX", "LIBSUFFIX"))
        # and .exp file is created if there are exports from a DLL
        extratargets.append(
            env.ReplaceIxes(dll,
                            "SHLIBPREFIX", "SHLIBSUFFIX",
                            "WINDOWSEXPPREFIX", "WINDOWSEXPSUFFIX"))

    return (target+extratargets, source+extrasources)

def prog_emitter(target, source, env):
    validate_vars(env)

    extratargets = []

    exe = env.FindIxes(target, "PROGPREFIX", "PROGSUFFIX")
    if not exe:
        raise SCons.Errors.UserError, "An executable should have exactly one target with the suffix: %s" % env.subst("$PROGSUFFIX")
    
    options = _EnvOptions( env )
    
    if options.cc_ver >= 8.0 and env.get('WINDOWS_INSERT_MANIFEST', 0):
        # MSVC 8 automatically generates .manifest files that have to be installed
        extratargets.append(
            env.ReplaceIxes(exe,
                            "PROGPREFIX", "PROGSUFFIX",
                            "WINDOWSPROGMANIFESTPREFIX", "WINDOWSPROGMANIFESTSUFFIX"))

    if env.has_key('PDB') and env['PDB']:
        pdb = env.arg2nodes('$PDB', target=target, source=source)[0]
        extratargets.append(pdb)
        target[0].attributes.pdb = pdb

    return (target+extratargets,source)

def RegServerFunc(target, source, env):
    if env.has_key('register') and env['register']:
        ret = regServerAction([target[0]], [source[0]], env)
        if ret:
            raise SCons.Errors.UserError, "Unable to register %s" % target[0]
        else:
            print "Registered %s sucessfully" % target[0]
        return ret
    return 0

regServerAction = SCons.Action.Action("$REGSVRCOM", "$REGSVRCOMSTR")
regServerCheck = SCons.Action.Action(RegServerFunc, None)
shlibLinkAction = SCons.Action.Action('${TEMPFILE("$SHLINK $SHLINKFLAGS $_SHLINK_TARGETS $( $_LIBDIRFLAGS $) $_LIBFLAGS $_PDB $_SHLINK_SOURCES")}')
compositeLinkAction = shlibLinkAction + regServerCheck

#//---------------------------------------------------------------------------//

def _add_msvc( env ):
    
    CSuffixes = ['.c', '.C']
    CXXSuffixes = ['.cc', '.cpp', '.cxx', '.c++', '.C++']
    
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)

    for suffix in CSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCAction)
        static_obj.add_emitter(suffix, static_object_emitter)
        shared_obj.add_emitter(suffix, shared_object_emitter)

    for suffix in CXXSuffixes:
        static_obj.add_action(suffix, SCons.Defaults.CXXAction)
        shared_obj.add_action(suffix, SCons.Defaults.ShCXXAction)
        static_obj.add_emitter(suffix, static_object_emitter)
        shared_obj.add_emitter(suffix, shared_object_emitter)

    env['CCPDBFLAGS'] = SCons.Util.CLVar(['${(PDB and "/Z7") or ""}'])
    env['CCPCHFLAGS'] = SCons.Util.CLVar(['${(PCH and "/Yu%s /Fp%s"%(PCHSTOP or "",File(PCH))) or ""}'])
    env['CCCOMFLAGS'] = '$CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS /c $SOURCES /Fo$TARGET $CCPCHFLAGS $CCPDBFLAGS'
    env['CC']         = 'cl'
    env['CCFLAGS']    = SCons.Util.CLVar('/nologo')
    env['CFLAGS']     = SCons.Util.CLVar('')
    env['CCCOM']      = '$CC $CFLAGS $CCFLAGS $CCCOMFLAGS'
    env['SHCC']       = '$CC'
    env['SHCCFLAGS']  = SCons.Util.CLVar('$CCFLAGS')
    env['SHCFLAGS']   = SCons.Util.CLVar('$CFLAGS')
    env['SHCCCOM']    = '$SHCC $SHCFLAGS $SHCCFLAGS $CCCOMFLAGS'
    env['CXX']        = '$CC'
    env['CXXFLAGS']   = SCons.Util.CLVar('$CCFLAGS $( /TP $)')
    env['CXXCOM']     = '$CXX $CXXFLAGS $CCCOMFLAGS'
    env['SHCXX']      = '$CXX'
    env['SHCXXFLAGS'] = SCons.Util.CLVar('$CXXFLAGS')
    env['SHCXXCOM']   = '$SHCXX $SHCXXFLAGS $CCCOMFLAGS'
    env['CPPDEFPREFIX']  = '/D'
    env['CPPDEFSUFFIX']  = ''
    env['INCPREFIX']  = '/I'
    env['INCSUFFIX']  = ''
    env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1

    env['RC'] = 'rc'
    env['RCFLAGS'] = SCons.Util.CLVar('')
    env['RCCOM'] = '$RC $_CPPDEFFLAGS $_CPPINCFLAGS $RCFLAGS /fo$TARGET $SOURCES'
    env['BUILDERS']['RES'] = res_builder
    env['OBJPREFIX']      = ''
    env['OBJSUFFIX']      = '.obj'
    env['SHOBJPREFIX']    = '$OBJPREFIX'
    env['SHOBJSUFFIX']    = '$OBJSUFFIX'

    env['CFILESUFFIX'] = '.c'
    env['CXXFILESUFFIX'] = '.cc'

    env['PCHPDBFLAGS'] = SCons.Util.CLVar(['${(PDB and "/Yd") or ""}'])
    env['PCHCOM'] = '$CXX $CXXFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS /c $SOURCES /Fo${TARGETS[1]} /Yc$PCHSTOP /Fp${TARGETS[0]} $CCPDBFLAGS $PCHPDBFLAGS'
    env['BUILDERS']['PCH'] = pch_builder

    if not env.has_key('ENV'):
        env['ENV'] = {}
    if not env['ENV'].has_key('SystemRoot'):    # required for dlls in the winsxs folders
        env['ENV']['SystemRoot'] = str( SCons.Platform.win32.get_system_root() )

#//---------------------------------------------------------------------------//

def _add_mslink( env ):
    """Add Builders and construction variables for ar to an Environment."""
    SCons.Tool.createSharedLibBuilder(env)
    SCons.Tool.createProgBuilder(env)

    env['SHLINK']      = '$LINK'
    env['SHLINKFLAGS'] = SCons.Util.CLVar('$LINKFLAGS /dll')
    env['_SHLINK_TARGETS'] = windowsShlinkTargets
    env['_SHLINK_SOURCES'] = windowsShlinkSources
    env['SHLINKCOM']   =  compositeLinkAction
    env.Append(SHLIBEMITTER = [windowsLibEmitter])
    env['LINK']        = 'link'
    env['LINKFLAGS']   = SCons.Util.CLVar('/nologo')
    env['_PDB'] = pdbGenerator
    env['LINKCOM'] = '${TEMPFILE("$LINK $LINKFLAGS /OUT:$TARGET.windows $( $_LIBDIRFLAGS $) $_LIBFLAGS $_PDB $SOURCES.windows")}'
    env.Append(PROGEMITTER = [prog_emitter])
    env['LIBDIRPREFIX']='/LIBPATH:'
    env['LIBDIRSUFFIX']=''
    env['LIBLINKPREFIX']=''
    env['LIBLINKSUFFIX']='$LIBSUFFIX'

    env['WIN32DEFPREFIX']        = ''
    env['WIN32DEFSUFFIX']        = '.def'
    env['WIN32_INSERT_DEF']      = 0
    env['WINDOWSDEFPREFIX']      = '${WIN32DEFPREFIX}'
    env['WINDOWSDEFSUFFIX']      = '${WIN32DEFSUFFIX}'
    env['WINDOWS_INSERT_DEF']    = '${WIN32_INSERT_DEF}'

    env['WIN32EXPPREFIX']        = ''
    env['WIN32EXPSUFFIX']        = '.exp'
    env['WINDOWSEXPPREFIX']      = '${WIN32EXPPREFIX}'
    env['WINDOWSEXPSUFFIX']      = '${WIN32EXPSUFFIX}'

    env['WINDOWSSHLIBMANIFESTPREFIX'] = ''
    env['WINDOWSSHLIBMANIFESTSUFFIX'] = '${SHLIBSUFFIX}.manifest'
    env['WINDOWSPROGMANIFESTPREFIX']  = ''
    env['WINDOWSPROGMANIFESTSUFFIX']  = '${PROGSUFFIX}.manifest'

    env['REGSVRACTION'] = regServerCheck
    env['REGSVR'] = os.path.join(SCons.Platform.win32.get_system_root(),'System32','regsvr32')
    env['REGSVRFLAGS'] = '/s '
    env['REGSVRCOM'] = '$REGSVR $REGSVRFLAGS ${TARGET.windows}'

    # For most platforms, a loadable module is the same as a shared
    # library.  Platforms which are different can override these, but
    # setting them the same means that LoadableModule works everywhere.
    SCons.Tool.createLoadableModuleBuilder(env)
    env['LDMODULE'] = '$SHLINK'
    env['LDMODULEPREFIX'] = '$SHLIBPREFIX'
    env['LDMODULESUFFIX'] = '$SHLIBSUFFIX'
    env['LDMODULEFLAGS'] = '$SHLINKFLAGS'
    # We can't use '$SHLINKCOM' here because that will stringify the
    # action list on expansion, and will then try to execute expanded
    # strings, with the upshot that it would try to execute RegServerFunc
    # as a command.
    env['LDMODULECOM'] = compositeLinkAction

#//---------------------------------------------------------------------------//

def     _add_mslib( env ):
    
    SCons.Tool.createStaticLibBuilder(env)

    env['AR']          = 'lib'
    env['ARFLAGS']     = SCons.Util.CLVar('/nologo')
    env['ARCOM']       = "${TEMPFILE('$AR $ARFLAGS /OUT:$TARGET $SOURCES')}"
    env['LIBPREFIX']   = ''
    env['LIBSUFFIX']   = '.lib'

#//---------------------------------------------------------------------------//

def     _where_is_program( env, prog, normcase = os.path.normcase ):
    tool_path =  env.WhereIs( prog ) or SCons.Util.WhereIs( prog )
    
    if tool_path:
        return normcase( tool_path )
    else:
        _Info("'%s' has not been found." % (prog))
        _Info("PATH: %s" % (env['ENV']['PATH']))
    
    return tool_path

#//---------------------------------------------------------------------------//

def     _get_msvc_specs( env, options, bin_path, check_existence_only, msvc_specs_cache = {} ):
    
    cc_ver, target_machine = msvc_specs_cache.get( bin_path, (None, None) )
    
    #//-------------------------------------------------------//
    
    if cc_ver is None:
        
        os_env = os.environ.copy()
        _PrependEnvPath( os_env, 'PATH', env['ENV']['PATH'] )
        _PrependEnvPath( os_env, 'PATH', bin_path )
        
        cc_ver = None
        target_machine = None
        
        output = subprocess.Popen( 'link.exe /logo', shell=True, stdout=subprocess.PIPE, env = os_env ).stdout.readline().strip()
        match = re.search(r'Microsoft \(R\) Incremental Linker Version (?P<version>[0-9]+\.[0-9]+)', output )
        if match:
            cc_ver = match.group('version')
        
        output = subprocess.Popen( 'cl.exe /logo', shell=True, stderr=subprocess.PIPE, env = os_env ).stderr.readline().strip()
        match = re.search(r'Compiler Version [0-9.]+ for (?P<machine>.+)', output )
        if match:
            target_machine = match.group('machine')
        
        msvc_specs_cache[ bin_path ] = ( cc_ver, target_machine )
    
    #//-------------------------------------------------------//
    
    if not cc_ver:
        
        return 0
    
    target_os = 'windows'
    target_os_release = ''
    target_os_version = ''
    
    if not target_machine:
        target_machine = 'i386'
    
    target_cpu = ''
    
    if options.cc_ver               != cc_ver or \
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
        
        options.cc_name = 'msvc'
        options.cc_ver = cc_ver
    
    return 1

#//---------------------------------------------------------------------------//

def     _try( env, options, check_existence_only = 0 ):
    
    if (options.cc_name != 'msvc') or (options.target_os != 'windows'):
        _Info( "Wrong 'cc_name (%s)' or 'target_os (%s)'" % (options.cc_name, options.target_os) )
        return 0
    
    cl_path = _where_is_program( env, 'cl' )
    if not cl_path:
        return 0
    
    bin_path = os.path.dirname( cl_path )
    
    if not env.WhereIs('link', bin_path ):
        _Info( "'link' has been not found" )
        return 0
    
    if not env.WhereIs('lib', bin_path ):
        _Info( "'lib' has been not found." )
        return 0
    
    if not _get_msvc_specs( env, options, bin_path, check_existence_only ):
        _Info( "MS VC specs mismatch." )
        return 0
    
    if not check_existence_only:
        
        env.PrependENVPath('PATH', bin_path )
        
        _add_msvc( env )
        _add_mslink( env )
        _add_mslib( env )
    
    return 1

#//---------------------------------------------------------------------------//

def     generate( env ):
    
    options = _EnvOptions(env)
    
    if not _try( env, options ):
        return
    
    _setup_flags( options )

#//---------------------------------------------------------------------------//

def     exists( env ):
    return _try( env, _EnvOptions(env), check_existence_only = 1 )

