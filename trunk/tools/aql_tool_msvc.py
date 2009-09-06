
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

import SCons.Tool
import SCons.Util

import aql.utils
import aql.options
import aql.logging

_EnvOptions = aql.options.EnvOptions
_PrependEnvPath = aql.utils.prependEnvPath
_Info = aql.logging.Info
_Error = aql.logging.Error

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

def     _get_msvc_specs( env, options, msvc_specs_cache = {} ):
    
    bin_path = _where_is_program( env, 'cl' )
    
    cc_ver, target_machine = msvc_specs_cache.get( bin_path, (None, None) )
    
    #//-------------------------------------------------------//
    
    if cc_ver is None:
        
        #~ os_env = os.environ.copy()
        os_env = {}
        for k,v in env['ENV'].iteritems():
            os_env[k] = str(v)
        
        #~ _PrependEnvPath( os_env, 'PATH', env['ENV']['PATH'] )
        
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
    
    target_os = 'windows'
    target_os_release = ''
    target_os_version = ''
    
    if not target_machine:
        target_machine = 'i386'
    
    target_cpu = ''
    
    options.target_os = target_os
    options.target_os_release = target_os_release
    options.target_os_version = target_os_version
    options.target_machine = target_machine
    options.target_cpu = target_cpu
    
    options.cc_name = 'msvc'
    options.cc_ver = cc_ver
    
    return 1

#//---------------------------------------------------------------------------//

def     _try( env, options, check_existence_only = False ):
    if (options.cc_name != 'msvc') or (options.target_os != 'windows'):
        _Info( "Wrong 'cc_name (%s)' or 'target_os (%s)'" % (options.cc_name, options.target_os) )
        return False
    
    cc_ver = options.cc_ver
    
    if cc_ver:
        found = False
        from SCons.Tool.MSCommon.vs import query_versions
        for v in query_versions():
            if cc_ver == v:
                env['MSVS_VERSION'] = v
                found = True
                break
        
        if not found:
            if check_existence_only:
                return False
            else:
                _Error( "Version '%s' of Visual Studio has not been found" % (cc_ver) )
    
    if options.target_machine:
        if   options.target_machine == 'x86-32':    env['MSVS_ARCH'] = 'x86'
        elif options.target_machine == 'x86-64':    env['MSVS_ARCH'] = 'amd64'
    
    if check_existence_only:
        if SCons.Tool.FindAllTools(['msvc', 'mslib', 'mslink'], env ):
            return True
        return False
    
    env.Tool('msvc')
    env.Tool('mslib')
    env.Tool('mslink')
    
    _get_msvc_specs( env, options )
    
    return True

#//---------------------------------------------------------------------------//

def     generate( env ):
    _try( env, _EnvOptions(env) )

#//---------------------------------------------------------------------------//

def     exists( env ):
    return _try( env, _EnvOptions(env), check_existence_only = 1 )

