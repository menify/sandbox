import os.path
import SCons.Util

def     _quote_spaces( arg ):
    arg = str(arg)
    
    if (' ' in arg) or ('\t' in arg):
        return '"%s"' % arg
    else:
        return arg

#//---------------------------------------------------------------------------//

def     _convert_defines( defines ):
    args_defines = []
    
    for d in defines:
        if isinstance( d, (tuple, list) ):
            macro = d[0]
            value = d[1]
        else:
            eq_pos = d.find('=')
            if eq_pos != -1:
                macro = d[:eq_pos]
                value = d[eq_pos + 1:]
            else:
                macro = d
                value = None
        
        if value:
            value = value.strip()
            if value:
                if value[0] != '"':
                    args_defines.append( _quote_spaces( macro + '=' + value ) )
                else:
                    args_defines.append( macro + '=' + value )
        
        if not value:
            args_defines.append( macro )
    
    return args_defines


#//---------------------------------------------------------------------------//

import re
import subprocess

cxx_define_re = re.compile('#define\s+([_a-zA-Z]\w*)\s+(.*)')

def     _getCompilerPredefines( target, source, env ):
    
    if env.aqlOptions().cc_name != 'gcc':
        return ([],[])
    
    dummy_file = os.path.join( os.path.dirname( target[0].abspath ), '__lint_empty__.cpp' )
    
    if not os.path.isfile( dummy_file ):
        open( dummy_file, 'w').close()
    
    cxx_pp = subprocess.Popen( env.subst('$CXX $CXXFLAGS $CCFLAGS -v -dM -E') + ' ' + dummy_file,
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env = env['ENV'] )
    
    cxx_defines = cxx_pp.stdout
    cxx_includes = cxx_pp.stderr
    
    pre_defines = []
    
    for d in cxx_defines:
        match = cxx_define_re.match( d )
        if match:
            macro, value = match.groups()
            pre_defines.append( macro + '=' + value.strip())
    
    pre_cpppath = []
    start_include = False
    for l in cxx_includes:
        l = l.strip()
        
        if not start_include:
            if l  == "#include <...> search starts here:":
                start_include = True
        else:
            if l == "End of search list.":
                break
            else:
                pre_cpppath.append( os.path.normpath(l) )
    
    return (pre_defines, pre_cpppath)

#//---------------------------------------------------------------------------//

def     _create_src_lnt( target, source, env, for_signature, lint_glob ):
    
    target_lnt_file = target[0].abspath + '.lnt'
    
    if not for_signature:
        cpp_defines = map( str, env.subst_list( '$CPPDEFINES' )[0] )
        
        pre_defines, pre_cpppath = _getCompilerPredefines( target, source, env )
        
        cpp_defines = pre_defines + cpp_defines
        cpp_defines = _convert_defines( cpp_defines )
        
        defines = [ '-d' + m for m in cpp_defines ]
        
        paths = env.subst_list( '$CPPPATH' )[0]
        paths += env.aqlOptions().cpppath_lib.Value()
        
        paths = map( lambda p: os.path.abspath( str(p)), paths )
        
        paths = [ '-i' + d for d in map( _quote_spaces, paths ) ]
        paths += [ '--i' + d for d in map( _quote_spaces, pre_cpppath ) ]
        
        sources = [ os.path.abspath( str(s) ) for s in source ]
        
        args = []
        
        args += defines
        args += paths
        args += map( _quote_spaces, sources )
        
        if lint_glob:
            undefines = [ '-u' + m for m in cpp_defines ]
            args += undefines
            args += ['-i-']
        
        f = open( target_lnt_file, 'w')
        f.write( '\n'.join( args ) + "\n" )
        f.close()
    
    return target_lnt_file

#//---------------------------------------------------------------------------//

def     _create_lib_lnt( target, source, for_signature, lint_glob ):
    
    target_lnt_file = target[0].abspath + '.lnt'
    
    if not for_signature:
        lnt_files = []
        
        for s in source:
            if lint_glob:
                lnt_file = s.abspath + '.lnt'
            else:
                lnt_file = s.abspath + '.lnt'
                if not os.path.isfile( lnt_file ):
                    lnt_file = s.abspath + '.lnt'
            
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
        
        lint_glob = (options.lint == 'global')
        
        if self.file_type == "src":
            target_lnt_file = _create_src_lnt( target, source, env, for_signature, lint_glob )
            
            if not lint_glob:
                target_lob_file = '-oo(' + target[0].abspath + '.lob' + ')'
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
    if_msvc_ver['9.0'].lint_flags  += 'co-msc90.lnt'
    
    if_cc_name['wcc'].lint_flags += 'co-wc32.lnt'
    if_cc_name['gcc'].lint_flags += 'co-gcc.lnt'
    
    if_cc_name['gcc'].lint_flags += '--u_GLIBCXX_CONCEPT_CHECKS'

def exists(env):
    return _find_it( env )
