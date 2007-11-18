
import sys, os.path
sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..' ) )

import options
import builtin_options

del sys.path[0]

_Options = options.Options
_StrOption = options.StrOption
_IntOption = options.IntOption
_PathOption = options.PathOption
_EnumOption = options.EnumOption
_VersionOption = options.VersionOption
_BoolOption = options.BoolOption
_BuiltinOptions = builtin_options.BuiltinOptions

_EnvOptions = options.EnvOptions

options = _Options()

bool_opt = _BoolOption( 'false'  )
options.bool_opt = bool_opt
options.bool_opt = bool_opt
options.bool_opt = bool_opt

options.bool_opt = 'true'

assert bool_opt == 'true'

a = 1

def     a_condition2( options ):
    global a
    
    if a == 2:
        return 1
    else:
        return 0

bool_opt.SetIf( a_condition2, 'false' )


def     a_condition3( options ):
    global a
    
    if a == 3:
        return 1
    else:
        return 0

bool_opt.SetIf( a_condition3, 'false' )

assert bool_opt == 'true'
a = 2
assert bool_opt == 'false'
a = 3
assert bool_opt == 'false'
a = 4
assert bool_opt == 'true'

#//---------------------------------------------------------------------------//

int_opt = _IntOption( 0, min = 0, max = 5, is_list = 1 )
options.int_opt = int_opt
options.int_opt = int_opt

int_opt.Append( 3 );
int_opt.Append( 5 );
int_opt.AppendIf( a_condition2, 4 )
int_opt.AppendIf( a_condition3, 1 )
int_opt.RemoveIf( a_condition3, 3 )

assert 3 in int_opt
assert 5 in int_opt
assert 4 not in int_opt
a = 2
assert 3 in int_opt
assert 4 in int_opt
a = 3
assert 1 in int_opt
assert 4 not in int_opt
assert 3 not in int_opt

#//===========================================================================//
#//===========================================================================//

opt = _BuiltinOptions()

assert opt.build_variant == 'debug'

opt.optim = 'size'

opt.If().optim['size'].debug_symbols = 'off'

assert opt.debug_symbols == 'off'

opt.If().optim['off'].inline = 'off'

c = opt.If().optim['size']
c.debug_symbols['off'].inline = 'on'

assert opt.inline == 'on'

c.lint = 'single'

assert opt.lint == 'single'

opt.If().optim['speed'].inline = 'full'

#~ opt.If().warn.ge(3).warn_err = 'true'
#~ opt.If().warn.ge(2).warn.le(4).warn_err = 'true'
#~ opt.If().warn(2,4).warn_err = 'true'

opt.If().warn_err['true'].warn = 4

opt.If().warn_err.eq('true').warn = 4

opt.If()['warn_err'].eq('true').warn = 4

opt.optim = 'off'
assert opt.debug_symbols == 'on'
assert opt.inline == 'off'
assert opt.lint == 'off'

opt.optim = 'size'
assert opt.inline == 'on'
assert opt.lint == 'single'

opt.optim = 'speed'
assert opt.inline == 'full'
assert opt.lint == 'off'



opt.defines = _StrOption( is_list = 1 )

opt.If().optim.ne('off').defines += 'RELEASE'
opt.If().optim['off'].defines += [ 'DEBUG' ]

opt.defines += 'PROF'

opt.optim = 'off'
assert opt.defines == [ 'DEBUG', 'PROF' ]

opt.optim = 'size'
assert opt.defines == [ 'RELEASE', 'PROF' ]

opt.optim = 'speed'
assert opt.defines == [ 'RELEASE', 'PROF' ]


opt.path = _PathOption( [], is_list = 1 )

opt.path += '../test/../src;test/..'
opt.path += '../test/../src/lib'

assert opt.path == [ '../src', '.', '../src/lib' ]


opt.build_variant = 'debug'

env1 = opt.LinkToKW( ccflags = '-O9', defines = 'USE_LOCAL_1', build_variant = 'release' )
env2 = opt.LinkToKW( ccflags = '-g', defines = 'USE_LOCAL_2' )

assert '-O9' not in opt.ccflags
assert '-g'  not in opt.ccflags
assert 'USE_LOCAL_1' not in opt.defines
assert 'USE_LOCAL_2' not in opt.defines
assert opt.build_variant == 'debug'

env = env1.copy()
env.update( env2 )

env['MPC_OPTIONS'] = opt
env_opt = _EnvOptions( env )

assert '-O9' in env_opt.ccflags
assert '-g'  in env_opt.ccflags
assert 'USE_LOCAL_1' in env_opt.defines
assert 'USE_LOCAL_2' in env_opt.defines
assert env_opt.build_variant == 'release'
#~ assert opt.build_variant == 'debug'


#//===========================================================================//

opt.runtime_linking = 'shared'
opt.lint_passes = 3

env1 = {}
opt.LinkToEnv( env1 )

opt.runtime_linking = 'static'

assert opt.runtime_linking == 'shared'

env2 = env1.copy()

opt.LinkToEnv( env2 )
opt.lint_passes = 4

assert opt.runtime_linking == 'shared'
assert opt.lint_passes == 3

opt.UnlinkToEnv()

assert opt.runtime_linking == 'shared'
assert opt.lint_passes == 3

env2['MPC_OPTIONS'] = opt
env_opt = _EnvOptions( env2 )

assert env_opt.runtime_linking == 'static'
assert env_opt.lint_passes == 4

assert opt.runtime_linking == 'shared'
assert opt.lint_passes == 3

opt.UnlinkToEnv()

assert opt.runtime_linking == 'shared'
assert opt.lint_passes == 3

#//===========================================================================//

assert '-O9' not in opt.ccflags
assert '-g'  not in opt.ccflags
assert 'USE_LOCAL_1' not in opt.defines
assert 'USE_LOCAL_2' not in opt.defines
assert opt.build_variant == 'debug'

opt.defines += opt.build_variant
print opt.defines.Get()

assert opt.defines == 'RELEASE PROF debug'

opt.build_variant = 'release'
assert opt.defines == 'RELEASE PROF release_speed'

print opt.build_dir
assert str(opt.build_dir) == 'build//release_speed'

opt.cc_name = 'gcc'
opt.cc_ver = '4.2.1'
opt.target_os = 'linux'
opt.target_machine = 'arm'
assert str(opt.build_dir) == 'build/linux_arm_gcc-4.2.1/release_speed'

opt.target_os = 'linux'
opt.target_cpu = 'arm1136j-s'
assert str(opt.build_dir) == 'build/linux_arm-arm1136j-s_gcc-4.2.1/release_speed'


def     BuildDir( options, bv_id ):
    import os.path
    
    bv = options.build_variant
    bv.Set( bv_id )
    
    build_dir = os.path.normpath( str( options.build_dir ) )
    
    bv.Undo()
    
    return build_dir

print opt.build_variant
print BuildDir( opt, 'debug' )
print BuildDir( opt, 'release_speed' )
print BuildDir( opt, 'release_size' )
print opt.build_variant
