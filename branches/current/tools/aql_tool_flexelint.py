import os.path
import SCons.Util

def     _quote_spaces( arg ):
    if ' ' in arg or '\t' in arg:
        return '"%s"' % arg
    else:
        return str(arg)

#//---------------------------------------------------------------------------//

def     _lnt_file( file ):
    return os.path.abspath( str( file ) ) + '.lnt'

#//---------------------------------------------------------------------------//

def     _lob_file( file ):
    return os.path.abspath( str( file ) ) + '.lob'

#//---------------------------------------------------------------------------//

def     _create_src_lnt( target, source, env, for_signature, lint_glob ):
    
    target_lnt_file = _lnt_file( target[0] )
    
    if not for_signature:
        
        cpp_defines = env.subst_list( '$CPPDEFINES' )[0]
        defines = [ '-d' + m for m in cpp_defines ]
        
        paths = env.subst_list( '$CPPPATH' )[0]
        
        paths += env.aqlOptions().cpppath_lib.Value()
        
        paths = [ '-i' + os.path.abspath( str(d) ) for d in paths ]
        
        sources = [ os.path.abspath( str(s) ) for s in source ]
        
        args = []
        
        args += map( _quote_spaces, defines )
        args += map( _quote_spaces, paths )
        args += map( _quote_spaces, sources )
        
        if lint_glob:
            undefines = [ '-u' + m for m in cpp_defines ]
            args += map( _quote_spaces, undefines )
            args += map( _quote_spaces, ['-i-'] )
            
        f = open( target_lnt_file, 'w')
        f.write( " ".join( args ) + "\n" )
        f.close()
    
    return target_lnt_file

#//---------------------------------------------------------------------------//

def     _create_lib_lnt( target, source, for_signature, lint_glob ):
    
    target_lnt_file = _lnt_file( target[0] )
    
    if not for_signature:
    
        lnt_files = []
        
        for s in source:
            
            if lint_glob:
                lnt_file = _lnt_file( s )
            else:
                lnt_file = _lob_file( s )
                if not os.path.isfile( lnt_file ):
                    lnt_file = _lnt_file( s )
            
            if os.path.isfile( lnt_file ):
                lnt_files.append( lnt_file )
        
        f = open( target_lnt_file, 'w' )
        f.write( "\n".join( lnt_files ) )
        f.close()
    
    return target_lnt_file

#//---------------------------------------------------------------------------//

class _LintCom:
    
    def __init__( self, file_type ):
        self.file_type = file_type
    
    #//-------------------------------------------------------//
    
    def __call__(self, target, source, env, for_signature):
        
        options = env.aqlOptions()
        
        if options.lint == 'off':
            return []
        
        lint_glob = (options.lint == 'glob')
        
        if self.file_type == "src":
            target_lnt_file = _create_src_lnt( target, source, env, for_signature, lint_glob )
            
            if not lint_glob:
                target_lob_file = '-oo(' + _lob_file( target[0] ) + ')'
            else:
                target_lob_file = ''
        else:
            target_lnt_file = _create_lib_lnt( target, source, for_signature, lint_glob )
            target_lob_file = ''
        
        lint_cmd = [ env['FLINT'] ]
        lint_cmd += options.lint_flags.Value()
        
        if self.file_type != "exe":
            lint_cmd.append( '-u' )
        
        lint_cmd += [ target_lnt_file, target_lob_file ]
        
        return lint_cmd

#//---------------------------------------------------------------------------//

def     _where_is_program( env, prog, normcase = os.path.normcase ):
    
    tool_path =  env.WhereIs( prog ) or SCons.Util.WhereIs( prog )
    
    if tool_path:
        return normcase( tool_path )
    
    return tool_path

#//---------------------------------------------------------------------------//

def     _find_it( env ):
    
    if not (env.has_key('CCCOM') and env.has_key('CXXCOM') and \
            env.has_key('SHCCCOM') and env.has_key('SHCXXCOM') and \
            env.has_key('ARCOM') and env.has_key('LINKCOM') ):
        
        return None
    
    for p in ['lint-nt', 'flint']:
        path = _where_is_program( env, p )
        if path:
            break
    
    return path
    
#//---------------------------------------------------------------------------//

def generate(env):
    
    flint = _find_it( env )
    if not flint:
        return
    
    env['FLINT'] = flint
    
    env['FLINTCOM'] = _LintCom
    
    env['CCCOM']  = [env['CCCOM'],  '${FLINTCOM("src")}' ]
    env['CXXCOM']  = [env['CXXCOM'],  '${FLINTCOM("src")}' ]
    env['SHCCCOM']  = [env['SHCCCOM'],  '${FLINTCOM("src")}' ]
    env['SHCXXCOM']  = [env['SHCXXCOM'],  '${FLINTCOM("src")}' ]
    
    env['ARCOM'] = [ env['ARCOM'], '${FLINTCOM("lib")}' ]
    env['LINKCOM'] = [ env['LINKCOM'], '${FLINTCOM("exe")}' ]
    
    #//=======================================================//
    
    options = env.aqlOptions()
    
    if_cc_name = options.If().cc_name
    if_msvc_ver = if_cc_name['msvc'].cc_ver
    if_msvc_ver['6.0'].lint_flags  += 'co-msc60.lnt'
    if_msvc_ver['7.0'].lint_flags  += 'co-msc70.lnt'
    if_msvc_ver['7.1'].lint_flags  += 'co-msc71.lnt'
    if_msvc_ver['8.0'].lint_flags  += 'co-msc80.lnt'
    
    if_cc_name['wcc'].lint_flags   += 'co-wc32.lnt'
    if_cc_name['gcc'].target_os['windows'].lint_flags += 'co-mingw.lnt'

def exists(env):
    return _find_it( env )
