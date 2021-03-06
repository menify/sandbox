
import mpc_log
import mpc_options

_Error = mpc_log.Error
_Options = mpc_options.Options
_StrOption = mpc_options.StrOption
_IntOption = mpc_options.IntOption
_PathOption = mpc_options.PathOption
_EnumOption = mpc_options.EnumOption
_LinkedOption = mpc_options.LinkedOption
_VersionOption = mpc_options.VersionOption
_BoolOption = mpc_options.BoolOption

#//===========================================================================//

def     _add_build_options( options ):
    
    options.setup = _StrOption( separator = ',', is_list = 1, help = "Setup options" )
    
    options.build_dir = _StrOption( 'build/', help = "Build directory suffix", is_list = 1, separator = '', unique = 0 )

#//===========================================================================//

import sys
import platform

def     _add_platform_options( options ):
    
    options.target_os = _EnumOption( default = '', allowed_values = ( '', 'windows', 'linux', 'cygwin', 'darwin', 'java' ),
                                    help = "The system/OS name, e.g. 'Linux', 'Windows', or 'Java'." )
    
    options.target_os_release = _StrOption( default = '',
                                            ignore_case = 1,
                                            help = "The system's release, e.g. '2.2.0' or 'XP'" )
    
    options.target_os_version = _VersionOption( default = '',
                                                help = "The system's release version, e.g. '2.2.0' or '5.1.2600'" )
    
    options.target_machine = _EnumOption( default = '',
                                          allowed_values = ('', 'i386', 'x86-64','arm' ),
                                          aliases = {'i686':'i386','i586':'i386', 'pc':'i386'},
                                          help = "The machine type, e.g. 'i386'" )
    
    options.target_cpu = _StrOption( default = '',
                                     ignore_case = 1,
                                     help = "The real processor name, e.g. 'amdk6'." )
    
    options.target_cpu_flags = _StrOption( default = '',
                                     ignore_case = 1, is_list = 1,
                                     help = "The CPU flags, e.g. 'mmx', 'sse2'." )

#//===========================================================================//

def     _set_build_dir( options ):
    
    # build_dir = build/<target OS>_<target CPU>_<cc name><cc ver>/<build variant>
    
    bd_if = options.If()
    
    #//-------------------------------------------------------//
    # Add OS
    
    target_os_nzero = bd_if.target_os.ne('')
    target_os_nzero.build_dir += options.target_os
    
    target_os_release_nzero = target_os_nzero.target_os_release.ne('')
    target_os_release_nzero.build_dir += '-'
    target_os_release_nzero.build_dir += options.target_os_release
    
    target_os_release_nzero.target_os_version.ne('').build_dir += options.target_os_version
    
    target_os_nzero.build_dir += '_'
    
    #//-------------------------------------------------------//
    # Add CPU
    
    target_machine_nzero = bd_if.target_machine.ne('')
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

#//===========================================================================//

def     _add_variants( options ):
    
    build_variants = _EnumOption( 'debug', ('debug', 'release_speed', 'release_size', 'final'),
                                            {'release': 'release_speed'},
                                            separator = ',',
                                            help = "Active build variants", is_list = 1 )
    
    options.build_variants = build_variants
    options.builds = build_variants
    
    # 'all' build variant is added during the Build process
    # build_variants.AddAliases( 'all', build_variants.AllowedValues() )
    
    build_variant = _LinkedOption( default = 'debug',
                                   options = options,
                                   linked_opt_name = 'build_variants',
                                   help = "The current build variant." )
    
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
    
    optimization = _EnumOption(  'off', ('off', 'size', 'speed'),
                                        {'0': 'off', '1': 'size', '2': 'speed'},
                                        help = 'Compiler optimization level' )
    options.optimization = optimization
    options.opt = optimization
    options.optim = optimization
    options.O = optimization
    
    #//-------------------------------------------------------//
    
    inlining = _EnumOption( 'off', ('off', 'on', 'full'), help = 'Inline function expansion' )
    options.inlining = inlining
    options.inline = inlining
    
    #//-------------------------------------------------------//
    
    whole_optimization = _BoolOption( 'off', help = 'Whole program optimization' )
    options.whole_optimization = whole_optimization
    options.whole_opt = whole_optimization


#//===========================================================================//

def     _add_debug_options( options ):
    
    debug_symbols = _BoolOption( 'off', help = 'Include debug symbols' )
    options.debug_symbols = debug_symbols
    options.debug = debug_symbols
    
    #//-------------------------------------------------------//
    
    profiling = _BoolOption( 'disabled', help = 'Enable compiler profiling' )
    options.profiling = profiling
    options.prof = profiling


#//===========================================================================//

def     _add_warning_options( options ):
    
    warning_level = _IntOption( 4, min=0, max=4, help = 'Compiler warning level' )
    options.warning_level = warning_level
    options.warning = warning_level
    options.warn = warning_level
    options.wl = warning_level
    
    #//-------------------------------------------------------//
    
    warnings_as_errors = _BoolOption( 'off', help = 'Treat warnings as errors' )
    options.warnings_as_errors = warnings_as_errors
    options.warn_err = warnings_as_errors
    options.warn_as_err = warnings_as_errors
    options.we = warnings_as_errors

#//===========================================================================//

def     _add_code_generation_options( options ):
    
    user_interface = _EnumOption( 'console', ['console', 'gui'],
                                      help = 'Application user interface' )
    options.user_interface = user_interface
    options.ui = user_interface
    
    #//-------------------------------------------------------//
    
    options.rtti = _BoolOption( 'off', help = 'Enable C++ realtime type information' )
    
    #//-------------------------------------------------------//
    
    exception_handling = _BoolOption( 'on', help = 'Enable C++ exceptions handling' )
    options.exception_handling = exception_handling
    options.exceptions = exception_handling
    
    #//-------------------------------------------------------//
    
    keep_asm = _BoolOption( 'off', help = 'Keep generated assemblers files' )
    options.keep_asm = keep_asm
    options.asm = keep_asm

#//===========================================================================//

def     _add_runtime_options( options ):
    
    runtime_linking = _EnumOption( 'static', ['static', 'shared'], {'dynamic': 'shared'},
                                    help = 'Linkage type of runtime library' )
    options.runtime_linking = runtime_linking
    options.runtime_link = runtime_linking
    options.link_runtime = runtime_linking
    options.rtlink = runtime_linking
    
    #//-------------------------------------------------------//
    
    runtime_debugging = _BoolOption( 'no', help = 'Use debug version of runtime library' )
    options.runtime_debugging = runtime_debugging
    options.runtime_debug = runtime_debugging
    options.rt_debug = runtime_debugging
    
    #//-------------------------------------------------------//
    
    runtime_threading = _EnumOption( 'single', ['single', 'multi' ], help = 'Threading mode of runtime library' )
    options.runtime_threading = runtime_threading
    options.rt_threading = runtime_threading

#//===========================================================================//

def     _add_cc_options( options ):
    
    options.cflags = _StrOption( is_list = 1, help = "C compiler options" )
    options.ccflags = _StrOption( is_list = 1, help = "Common C/C++ compiler options" )
    options.cxxflags = _StrOption( is_list = 1, help = "C++ compiler options" )
    options.linkflags = _StrOption( is_list = 1, help = "Linker options" )
    
    options.cc_name = _StrOption( help = "C/C++ compiler name" )
    options.cc_ver = _VersionOption( help = "C/C++ compiler version" )
    
    options.gcc_prefix = _StrOption( help = "GCC C/C++ compiler prefix" )
    options.gcc_suffix = _StrOption( help = "GCC C/C++ compiler suffix" )
    
    options.cppdefines = _StrOption( is_list = 1, help = "C/C++ preprocessor defines" )
    options.cpppaths = _StrOption( is_list = 1, help = "C/C++ preprocessor paths to headers" )
    
    const_cpppaths = _StrOption( is_list = 1, help = "C/C++ preprocessor path to library headers" )
    options.const_cpppaths = const_cpppaths
    options.lib_cpppaths = const_cpppaths
    


#//===========================================================================//

def     _add_lint_options( options ):
    
    options.lint = _EnumOption( 'off', ['off', 'single', 'on', 'all'],
                                {'global': 'all', '0': 'off', '1':'single', '2':'on', '3':'all'},
                                help = 'Lint method' )
    
    #//-------------------------------------------------------//
    
    options.lint_passes = _IntOption( 3, min=1, help = 'The number of passes Flexelint makes over the source code' )
    
    options.lint_flags = _StrOption( is_list = 1, help = "Flexelint options" )

#//===========================================================================//

def     BuiltinOptions():
    
    options = _Options()
    
    prefix = '_add'
    prefix_len = len(prefix)
    suffix = '_options'
    suffix_len = len( suffix )
    
    local_names = globals()
    
    for name, function in local_names.iteritems():
        if (name[ 0 : prefix_len ] == prefix) and (name[ -suffix_len: ] == suffix ):
            function( options )
    
    _add_variants( options )
    
    return options
