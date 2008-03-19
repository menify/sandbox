
import os

import logging
import options
import local_host

_Error = logging.Error
_Options = options.Options
_StrOption = options.StrOption
_IntOption = options.IntOption
_PathOption = options.PathOption
_EnumOption = options.EnumOption
_LinkedOption = options.LinkedOption
_VersionOption = options.VersionOption
_BoolOption = options.BoolOption

#//===========================================================================//

def     _add_build_options( options ):
    
    aql_rootdir = os.path.dirname( __file__ )
    
    options.setup = _StrOption( separator = ',', is_list = 1,
                                help = "Setup options", group = "Builds setup" )
    
    options.build_dir = _StrOption( initial_value = 'build/', help = "The building directory prefix.",
                                    is_list = 1, separator = '', unique = 0, group = "Builds setup" )
    
    setup_path = os.environ.get('AQL_SETUP_PATH', aql_rootdir + '/setup' )
    options.setup_path = _PathOption( initial_value = setup_path, is_list = 1, update = 'Prepend',
                                      help = "A file path(s) to setup files.\n" \
                                             "By default environment variable AQL_SETUP_PATH is used.",
                                      group = "Builds setup" )
    
    options.tools = _StrOption( separator = ',', is_list = 1,
                                help = "Environment tools", group = "Builds setup" )
    
    tools_path = os.environ.get( 'AQL_TOOLS_PATH', aql_rootdir + '/tools' )
    options.tools_path = _PathOption( initial_value = tools_path, is_list = 1, update = 'Prepend',
                                      help = "A file path(s) to tools files.\n" \
                                             "By default environment variable AQL_TOOLS_PATH is used.",
                                      group = "Builds setup" )
    
    log_level = _IntOption( initial_value = 1, help = "AQL log level", group = "Builds setup" )
    options.log_level = log_level
    options.ll = log_level
    
    
#//===========================================================================//

def     _add_platform_options( options ):
    
    options.target_os = _EnumOption( allowed_values = ( 'windows', 'linux', 'cygwin', 'darwin', 'java', 'sunos', 'hpux' ),
                                     help = "The target system/OS name, e.g. 'Linux', 'Windows', or 'Java'.", group = "Platform" )
    
    options.target_platform = _StrOption( ignore_case = 1,
                                          help = "The system's distribution, e.g. 'win32', 'Linux'",
                                          group = "Platform")
    
    options.target_os_release = _StrOption( ignore_case = 1,
                                            help = "The target system's release, e.g. '2.2.0' or 'XP'",
                                            group = "Platform")
    
    options.target_os_version = _VersionOption( help = "The target system's release version, e.g. '2.2.0' or '5.1.2600'",
                                                group = "Platform")
    
    options.target_machine = _EnumOption( allowed_values = ('x86-32', 'x86-64','arm' ),
                                          aliases = {'i386':'x86-32','i586':'x86-32','i486':'x86-32','i686':'x86-32',
                                                     'i586':'x86-32', 'pc':'x86-32', 'x86':'x86-32'},
                                          help = "The target machine type, e.g. 'i386'", 
                                          group = "Platform" )
    
    options.target_cpu = _StrOption( ignore_case = 1,
                                     help = "The target real processor name, e.g. 'amdk6'.",
                                     group = "Platform" )
    
    options.target_cpu_flags = _StrOption( ignore_case = 1, is_list = 1,
                                           help = "The target CPU flags, e.g. 'mmx', 'sse2'.",
                                           group = "Platform" )
    
    if local_host.os:       options.target_os = local_host.os
    if local_host.machine:  options.target_machine = local_host.machine

#//===========================================================================//

def     _set_build_dir( options ):
    
    # build_dir = build/<target OS>_<target CPU>_<cc name><cc ver>/<build variant>
    
    bd_if = options.If()
    
    #//-------------------------------------------------------//
    # Add OS
    
    target_os_nzero = bd_if.target_os.ne( None )
    target_os_nzero.build_dir += options.target_os
    
    target_os_release_nzero = target_os_nzero.target_os_release.ne('')
    target_os_release_nzero.build_dir += '-'
    target_os_release_nzero.build_dir += options.target_os_release
    
    target_os_release_nzero.target_os_version.ne('').build_dir += options.target_os_version
    
    target_os_nzero.build_dir += '_'
    
    #//-------------------------------------------------------//
    # Add CPU
    
    target_machine_nzero = bd_if.target_machine.ne( None )
    target_machine_nzero.build_dir += options.target_machine
    
    target_cpu_nzero = target_machine_nzero.target_cpu.ne('')
    target_cpu_nzero.build_dir += '-'
    target_cpu_nzero.build_dir += options.target_cpu
    
    target_machine_nzero.build_dir += '_'
    
    #//-------------------------------------------------------//
    # add C/C++ compiler
    
    options.build_dir += options.cc_name
    
    cc_name_nzero = bd_if.cc_name.ne('')
    cc_name_nzero.build_dir += '-'
    cc_name_nzero.build_dir += options.cc_ver
    
    options.build_dir += '/'
    options.build_dir += options.build_variant
    
    bd_if.profiling['true'].build_dir += '_prof'

#//===========================================================================//

def     _add_variants( options ):
    
    build_variants = _EnumOption( initial_value = 'debug',
                                  allowed_values = ('debug', 'release_speed', 'release_size', 'final'),
                                  aliases = {'release': 'release_speed'},
                                  separator = ',',
                                  is_list = 1 ,
                                  update = 'Set',
                                  help = "Active build variants",
                                  group = "Build setup" )
    
    options.build_variants = build_variants
    options.builds = build_variants
    
    build_variants.AddAlias( 'all', build_variants.AllowedValues() )
    
    build_variant = _LinkedOption( initial_value = 'debug',
                                   options = options,
                                   linked_opt_name = 'build_variants',
                                   help = "The current build variant.",
                                   group = "Build setup" )
    
    options.build_variant = build_variant
    options.bv = build_variant
    
    _set_build_dir( options )
    
    if_bv = options.If().bv
    
    debug = if_bv['debug']
    debug.optimization          = 'off'
    debug.inlining              = 'off'
    debug.whole_optimization    = 'off'
    debug.debug_symbols         = 'on'
    debug.runtime_debugging     = 'on'
    
    release_speed = if_bv.one_of( ('release_speed', 'final') )
    release_speed.optimization          = 'speed'
    release_speed.inlining              = 'full'
    release_speed.whole_optimization    = 'on'
    release_speed.debug_symbols         = 'off'
    release_speed.runtime_debugging     = 'off'
    
    release_size = if_bv['release_size']
    release_size.optimization       = 'size'
    release_size.inlining           = 'on'
    release_size.whole_optimization = 'on'
    release_size.debug_symbols      = 'off'
    release_size.runtime_debugging  = 'off'

#//===========================================================================//

def     _add_optimization_options( options ):
    
    optimization = _EnumOption(  initial_value = 'off', allowed_values = ('off', 'size', 'speed'),
                                        aliases = {'0': 'off', '1': 'size', '2': 'speed'},
                                        help = 'Compiler optimization level',
                                        group = "Optimization" )
    options.optimization = optimization
    options.opt = optimization
    options.optim = optimization
    options.O = optimization
    
    #//-------------------------------------------------------//
    
    inlining = _EnumOption( initial_value = 'off', allowed_values = ('off', 'on', 'full'),
                            help = 'Inline function expansion', group = "Optimization" )
    options.inlining = inlining
    options.inline = inlining
    
    #//-------------------------------------------------------//
    
    whole_optimization = _BoolOption( initial_value = 'off', help = 'Whole program optimization', group = "Optimization" )
    options.whole_optimization = whole_optimization
    options.whole_opt = whole_optimization


#//===========================================================================//

def     _add_debug_options( options ):
    
    debug_symbols = _BoolOption( initial_value = 'off', help = 'Include debug symbols', group = "Debug" )
    options.debug_symbols = debug_symbols
    options.debug_info = debug_symbols
    options.debug = debug_symbols
    
    #//-------------------------------------------------------//
    
    profiling = _BoolOption( initial_value = 'disabled', help = 'Enable compiler profiling', group = "Debug" )
    options.profiling = profiling
    options.prof = profiling


#//===========================================================================//

def     _add_warning_options( options ):
    
    warning_level = _IntOption( initial_value = 4, min=0, max=4, help = 'Compiler warning level', group = "Warning")
    options.warning_level = warning_level
    options.warning = warning_level
    options.warn = warning_level
    options.wl = warning_level
    
    #//-------------------------------------------------------//
    
    warnings_as_errors = _BoolOption( initial_value = 'off', help = 'Treat warnings as errors', group = "Warning" )
    options.warnings_as_errors = warnings_as_errors
    options.warn_err = warnings_as_errors
    options.warn_as_err = warnings_as_errors
    options.we = warnings_as_errors

#//===========================================================================//

def     _add_code_generation_options( options ):
    
    user_interface = _EnumOption( initial_value = 'console', allowed_values = ['console', 'gui'],
                                  help = 'Application user interface', group = "Code generation" )
    options.user_interface = user_interface
    options.ui = user_interface
    
    #//-------------------------------------------------------//
    
    options.rtti = _BoolOption( initial_value = 'off', help = 'Enable C++ realtime type information', group = "Code generation" )
    
    #//-------------------------------------------------------//
    
    exception_handling = _BoolOption( initial_value = 'on', help = 'Enable C++ exceptions handling', group = "Code generation" )
    options.exception_handling = exception_handling
    options.exceptions = exception_handling
    
    #//-------------------------------------------------------//
    
    keep_asm = _BoolOption( initial_value = 'off', help = 'Keep generated assemblers files', group = "Code generation" )
    options.keep_asm = keep_asm
    options.asm = keep_asm

#//===========================================================================//

def     _add_runtime_options( options ):
    
    runtime_linking = _EnumOption( initial_value = 'static', allowed_values = ['static', 'shared'],
                                   aliases = {'dynamic': 'shared'},
                                    help = 'Linkage type of runtime library', group = "Runtime" )
    options.runtime_linking = runtime_linking
    options.runtime_link = runtime_linking
    options.link_runtime = runtime_linking
    options.rtlink = runtime_linking
    
    #//-------------------------------------------------------//
    
    runtime_debugging = _BoolOption( initial_value = 'no', help = 'Use debug version of runtime library', group = "Runtime" )
    options.runtime_debugging = runtime_debugging
    options.runtime_debug = runtime_debugging
    options.rt_debug = runtime_debugging
    
    #//-------------------------------------------------------//
    
    runtime_threading = _EnumOption( initial_value = 'single', allowed_values = ['single', 'multi' ],
                                     help = 'Threading mode of runtime library', group = "Runtime" )
    options.runtime_threading = runtime_threading
    options.rt_threading = runtime_threading

#//===========================================================================//

def     _add_cc_options( options ):
    
    options.cflags = _StrOption( is_list = 1, help = "C compiler options", group = "C/C++ compiler" )
    options.ccflags = _StrOption( is_list = 1, help = "Common C/C++ compiler options", group = "C/C++ compiler" )
    options.cxxflags = _StrOption( is_list = 1, help = "C++ compiler options", group = "C/C++ compiler" )
    options.linkflags = _StrOption( is_list = 1, help = "Linker options", group = "C/C++ compiler" )
    options.arflags = _StrOption( is_list = 1, help = "Archiver options", group = "C/C++ compiler" )
    
    options.ocflags = _StrOption( is_list = 1, help = "C compiler optimization options", group = "Optimization" )
    options.occflags = _StrOption( is_list = 1, help = "Common C/C++ compiler optimization options", group = "Optimization" )
    options.ocxxflags = _StrOption( is_list = 1, help = "C++ compiler optimization options", group = "Optimization" )
    options.olinkflags = _StrOption( is_list = 1, help = "Linker optimization options", group = "Optimization" )
    options.oarflags = _StrOption( is_list = 1, help = "Archiver optimization options", group = "Optimization" )
    
    options.cflags = options.ocflags
    options.ccflags = options.occflags
    options.cxxflags = options.ocxxflags
    options.linkflags = options.olinkflags
    options.arflags = options.oarflags
    
    options.cc_name = _StrOption( help = "C/C++ compiler name", group = "C/C++ compiler" )
    options.cc_ver = _VersionOption( help = "C/C++ compiler version", group = "C/C++ compiler" )
    
    options.gcc_path = _StrOption()
    options.gcc_target = _StrOption()
    options.gcc_prefix = _StrOption( help = "GCC C/C++ compiler prefix", group = "C/C++ compiler" )
    options.gcc_suffix = _StrOption( help = "GCC C/C++ compiler suffix", group = "C/C++ compiler" )
    
    options.cppdefines = _StrOption( is_list = 1, help = "C/C++ preprocessor defines", group = "C/C++ compiler" )
    options.cpppath = _PathOption( is_list = 1, help = "C/C++ preprocessor paths to headers", is_node = 1, group = "C/C++ compiler" )
    
    cpppath_lib = _PathOption( is_list = 1, help = "C/C++ preprocessor path to library headers", is_node = 1, group = "C/C++ compiler" )
    options.cpppath_const = cpppath_lib
    options.cpppath_lib = cpppath_lib
    
    options.libpath = _PathOption( is_list = 1, help = "Paths to libraries", is_node = 1, group = "C/C++ compiler" )
    options.libs = _StrOption( is_list = 1, help = "Libraries", group = "C/C++ compiler" )


#//===========================================================================//

def     _add_lint_options( options ):
    
    options.lint = _EnumOption( initial_value = 'off', allowed_values = ['off', 'single', 'on', 'all'],
                                aliases = {'global': 'all', '0': 'off', '1':'single', '2':'on', '3':'all'},
                                help = 'Lint method', group = "Lint" )
    
    #//-------------------------------------------------------//
    
    options.lint_passes = _IntOption( initial_value = 3, min=1, help = 'The number of passes Flexelint makes over the source code', group = "Lint" )
    
    options.lint_flags = _StrOption( is_list = 1, help = "Flexelint options", group = "Lint" )

#//===========================================================================//

def     BuiltinOptions():
    
    options = _Options()
    
    prefix = '_add'
    suffix = '_options'
    
    local_names = globals()
    
    for name, function in local_names.iteritems():
        if name.startswith( prefix ) and name.endswith( suffix ):
            function( options )
    
    _add_variants( options )
    
    return options
