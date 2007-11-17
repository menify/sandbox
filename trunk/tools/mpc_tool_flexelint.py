import os.path
import string

from mpc_env_options import MPC_EnvOptionsProxy

def     _quote_spaces( arg ):
    # Generic function for putting double quotes around any string that has white space in it.
    if ' ' in arg or '\t' in arg:
        return '"%s"' % arg
    else:
        return str(arg)
#//---------------------------------------------------------------------------//

def     _lnt_file( file ):
    filename, ext = os.path.splitext( os.path.abspath( str( file ) ) )
    
    return filename + '_' + ext[1:] + '.lnt'

#//---------------------------------------------------------------------------//

def     _lob_file( file ):
    filename, ext = os.path.splitext( os.path.abspath( str( file ) ) )
    
    return filename + '_' + ext[1:] + '.lob'

#//---------------------------------------------------------------------------//

def     _lint_options( env_opt ):
        
        lint_options = ['-b']
        
        if env_opt.has_key('lint_passes'):
            lint_options.append('-passes(' + str( env_opt['lint_passes'] ) + ')')
        
        if env_opt.has_key('warning_level'):
            lint_options.append( '-w' + str(env_opt['warning_level']) )
        
        if env_opt['warnings_as_errors'] == 'off':
            lint_options.append('-zero' )
        
        return lint_options

#//---------------------------------------------------------------------------//

def     _create_src_lnt( target, source, env, for_signature, lint_all ):
    
    target_lnt_file = _lnt_file( target[0] )
    
    if not for_signature:
        
        cpp_defines = env.subst_list( '$CPPDEFINES' )[0]
        defines = [ '-d' + m for m in cpp_defines ]
        
        paths = env.subst_list( '$CPPPATH' )[0]
        paths = [ '-i' + os.path.abspath( str(d) ) for d in paths ]
        
        sources = [ os.path.abspath( str(s) ) for s in source ]
        
        args = map( _quote_spaces, defines )
        args += map( _quote_spaces, paths )
        args += map( _quote_spaces, sources )
        
        if lint_all:
            undefines = [ '-u' + m for m in cpp_defines ]
            args += map( _quote_spaces, undefines )
            args += map( _quote_spaces, ['-i-'] )
            
            if env['ENV'].has_key('LINT'):
                env_lint = env.Split( env['ENV']['LINT'] )
                for o in env_lint:
                    if (o[:2] == '-i') or (o[:2] == '-I'):
                        args.append( o )
        
        f = open( target_lnt_file, 'w')
        f.write( string.join( args, " " ) + "\n" )
        f.close()
    
    return target_lnt_file

#//---------------------------------------------------------------------------//

def     _create_lib_lnt( target, source, for_signature, lint_all ):
    
    target_lnt_file = _lnt_file( target[0] )
    
    if not for_signature:
    
        lnt_files = []
        
        for s in source:
            
            if lint_all:
                lnt_file = _lnt_file( s )
            else:
                lnt_file = _lob_file( s )
                if not os.path.isfile( lnt_file ):
                    lnt_file = _lnt_file( s )
            
            if os.path.isfile( lnt_file ):
                lnt_files.append( lnt_file )
        
        f = open( target_lnt_file, 'w')
        f.write( string.join( lnt_files, "\n" ) )
        f.close()
    
    return target_lnt_file

#//---------------------------------------------------------------------------//

class _LintFile:
    
    def __init__( self, file_type ):
        self.file_type = file_type
    
    #//-------------------------------------------------------//
    
    def __call__(self, target, source, env, for_signature):
        
        env_opt = MPC_EnvOptionsProxy( env )
        
        if env_opt['lint'] == 'all':
            lint_all = 1
        
        elif env_opt['lint'] == 'on':
            lint_all = 0
        
        else:
            return []
        
        lint_options = _lint_options( env_opt )
        
        if self.file_type == "src":
            target_lnt_file = _create_src_lnt( target, source, env, for_signature, lint_all )
            
            if not lint_all:
                target_lob_file = '-oo(' + _lob_file( target[0] ) + ')'
            else:
                target_lob_file = ''
        else:
            target_lnt_file = _create_lib_lnt( target, source, for_signature, lint_all )
            target_lob_file = ''
        
        if self.file_type != "exe":
            lint_options.append( '-u' )
        
        return [ env['FLINT'], lint_options, target_lnt_file, target_lob_file ]

#//---------------------------------------------------------------------------//

def     _find_it( env ):
    return env.Detect( ['lint-nt', 'flint'] )
    
#//---------------------------------------------------------------------------//

def generate(env):
    
    env['FLINT'] = _find_it( env )
    
    env['FLINT_FILE'] = _LintFile
    
    env['CCCOM']  = [env['CCCOM'],  '${FLINT_FILE("src")}' ]
    env['CXXCOM']  = [env['CXXCOM'],  '${FLINT_FILE("src")}' ]
    env['SHCCCOM']  = [env['SHCCCOM'],  '${FLINT_FILE("src")}' ]
    env['SHCXXCOM']  = [env['SHCXXCOM'],  '${FLINT_FILE("src")}' ]
    
    env['ARCOM'] = [ env['ARCOM'], '${FLINT_FILE("lib")}' ]
    env['LINKCOM'] = [ env['LINKCOM'], '${FLINT_FILE("exe")}' ]

def exists(env):
    return _find_it( env )
