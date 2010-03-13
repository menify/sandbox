import sys
import os
import re
import os.path
import subprocess

def _normLocalPath( local_path ):
    
    npath = os.path.normpath( os.path.abspath( local_path ) )
    return npath.replace('\\', os.path.sep)

#//---------------------------------------------------------------------------//

class RemoteHost (object):
    __slots__ = ('login', 'password', 'host')
    
    def   __init__(self, login, password, host):
        self.login = login
        self.password = password
        self.host = host
    
    def   execRemote(self, remote_cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT ):
        cmd = 'plink.exe -batch -pw %s %s@%s %s' % (self.password, self.login, self.host, remote_cmd )
        return subprocess.Popen( cmd, shell = False, stdout = stdout, stderr = stderr, stdin = subprocess.PIPE )
    
    def   copy( self, local_path, remote_path, copy_to = True ):
        if copy_to:
            cmd = r'pscp.exe -i C:\work\settings\ssh_keys\neoa.root.ppk -pw %s %s %s@%s:%s'  % (self.password, local_path, self.login, self.host, remote_path )
        else:
            cmd = r'pscp.exe -i C:\work\settings\ssh_keys\neoa.root.ppk -pw %s %s@%s:%s %s'  % (self.password, self.login, self.host, remote_path, local_path )
        
        return subprocess.Popen( cmd, shell = False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin = subprocess.PIPE )
    
    def   normPath( self, remote_path ):
        #~ cmd = 'python -c \\"from os.path import *; print( normpath(abspath(%s)) )\\"' % repr(remote_path.replace('\\', '/'))
        #~ return self.execRemote( cmd ).stdout.readline().strip()
        return os.path.normpath( remote_path ).replace('\\', '/')
    
    def   joinPath( self, *args ):
        args = map( lambda a: a.replace('\\', '/'), args )
        cmd = 'python -c \\"from os.path import *; print( normpath(join(*%s)) )\\"' % repr(args)
        return self.execRemote( cmd ).stdout.readline().strip()

    def   exists( self, remote_path, working_path = '.', _cache = {} ):
        
        path_key = remote_path + working_path
        
        result = _cache.get( path_key )
        if result:
            return result
        
        cmd = 'python -c \\"from os.path import *; print( exists(abspath(join(%s, %s))) )\\"' % ( repr(working_path .replace('\\', '/')), repr(remote_path.replace('\\', '/')) )
        result = (self.execRemote( cmd ).stdout.readline().strip() == 'True')
        
        _cache[ path_key ] = result
        
        return result

#//-------------------------------------------------------//

_REMOTE_HOSTS = {
  'dev': RemoteHost( 'user', 'user', '10.64.74.147' ),
  'dev11': RemoteHost( 'c4dev', 'c4dev!', '10.64.74.114' ),
  'sim': RemoteHost( 'root', 'c4proto!', '10.64.75.91' ),
  'magnum205-spa': RemoteHost( 'root', 'c4proto!', '10.64.75.185' ),
  'magnum205-spb': RemoteHost( 'root', 'c4proto!', '10.64.75.186' ),
}

#//---------------------------------------------------------------------------//

class   RemotePathMapping (object):
    __slots__ = ( 'local_root', 'remote_root', 'host_data' )
    
    def   __init__(self, local_root, remote_root, host_data ):
        self.local_root = _normLocalPath( local_root )
        self.remote_root = remote_root
        self.host_data = host_data
    
    def   getRemotePath( self, local_path, _cache = {} ):
        path_key = local_path
        result = _cache.get( path_key )
        if result:
            return result
        
        local_path = _normLocalPath( local_path )
        assert local_path.startswith( self.local_root )
        rel_path = local_path[ len(self.local_root): ].strip( os.path.sep )
        
        result = self.host_data.joinPath( self.remote_root, rel_path )
        
        _cache[ path_key ] = result
        
        return result
    
    def   getLocalPath( self, remote_path,  _cache = {} ):
        path_key = remote_path
        result = _cache.get( path_key )
        if result:
            return result
        
        remote_path = self.host_data.normPath( remote_path )
        assert remote_path.startswith( self.remote_root )
        
        rel_path = remote_path[ len(self.remote_root): ].strip( '/\\' )
        result = _normLocalPath( os.path.join( self.local_root, rel_path ) )
        
        _cache[ path_key ] = result
        
        return result

#//-------------------------------------------------------//

_REMOTE_PATH_MAPS = [
  #~ RemotePathMapping( "W:\\", "/sources/", _REMOTE_HOSTS['dev'] ),
  RemotePathMapping( "\\\\10.64.74.147\\sources\\", "/sources/", _REMOTE_HOSTS['dev'] ),
  RemotePathMapping( "\\\\10.64.74.114\\work\\", "/work/", _REMOTE_HOSTS['dev11'] ),
  ]
  # key = lambda x: len(x.local_root), reverse = True )

#//---------------------------------------------------------------------------//

def   getMappingByLocalPath( local_path ):
    local_path = _normLocalPath( local_path )
    
    for path_map in _REMOTE_PATH_MAPS:
        if local_path.startswith( path_map.local_root ):
            return path_map
    
    return None

def   getMappingByRemotePath( remote_path ):
    
    for path_map in _REMOTE_PATH_MAPS:
        if remote_path.startswith( path_map.remote_root ):
            return path_map
    
    return None

#//---------------------------------------------------------------------------//

class SvnInfo (object):
    __slots__ = ( 'rel_url', 'revision', 'type' )
    
    def   __init__( self, path, host_data = None ):
        
        self.rel_url = None
        self.revision = None
        self.type = None
        
        if host_data:
            svn_info = host_data.execRemote( 'svn info ' + path )
        else:
            svn_info = subprocess.Popen( 'svn info ' + path, shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        
        svn_info.wait()
        
        url = None
        root = None
        
        for l in svn_info.stdout:
            l = l.strip()
            if l.startswith("URL: "):
                url = l[len("URL: "):].strip()
            
            elif l.startswith("Repository Root: "):
                root = l[len("Repository Root: "):].strip()
            
            elif l.startswith("Revision: "):
                self.revision = l[len("Revision: "):].strip()
            
            elif l.startswith("Node Kind: "):
                self.type = l[len("Node Kind: "):].strip()
        
        if url and root:
            self.rel_url = url[ len(root) : ].strip('/')
    
    def     __cmp__( self, other ):
        for s in self.__slots__:
            r = cmp( getattr(self, s), getattr(other, s) )
            if r != 0:
                return r
        return r
    
    def     __str__(self):
        return self.url
    
    def     diffAttr( self, other ):
        for s in self.__slots__:
            if cmp( getattr(self, s), getattr(other, s) ):
                return s
        return None

#//---------------------------------------------------------------------------//

def   _printFile( file ):
    for l in file:
        sys.stdout.write(l)

def   copyRemote( local_path, copy_to = True ):
    m = getMappingByLocalPath( local_path )
    if m:
        remote_path = m.getRemotePath( local_path )
        out = m.host_data.copy( local_path, remote_path, copy_to )
        out.wait()
        _printFile( out.stderr )
        
        local_svn = SvnInfo( local_path )
        remote_svn = SvnInfo( remote_path, m.host_data )
        diff_attr = local_svn.diffAttr( remote_svn )
        if diff_attr:
            lattr = getattr(local_svn, diff_attr)
            rattr = getattr(remote_svn, diff_attr)
            sys.stderr.write( "Warning: Subversion mismatch: %s: %s (local) != %s (remote)\n" % (diff_attr, lattr, rattr) )

#//---------------------------------------------------------------------------//

def     _findBuildXml( path ):
    
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    
    while True:
        if 'build.xml' in os.listdir(path):
            return path
        
        prev_path = path
        path = os.path.dirname(path)
        if prev_path == path:
            return None

def     _antPrefixFilter( s, ant_redundant_re = re.compile( r"^\s+\[[a-z]+\]" ) ):
    m = ant_redundant_re.search( s )
    if m:
        s = s[ m.end():]
    return s

def     _mapFilePaths( s, host_data, build_path, file_path_re = re.compile( r"[\w\.\\/]*/[\w\-\.\\/]+" ), line_num_re = re.compile(r":(\d+):") ):
    pos = 0
    mapped_s = ''
    
    for m in file_path_re.finditer( s ):
        file_path = s[m.start():m.end()]
        
        if file_path.startswith('../'):
          file_path_list = file_path.split('/')
          while True:
              local_file_path = os.path.normpath( os.path.join( build_path, *file_path_list ) )
              if os.path.exists( local_file_path ):
                  file_path = local_file_path
                  break
              
              if (len(file_path_list) < 2) or file_path_list[1] != '..':
                  break
              file_path_list = file_path_list[1:]
        else:
            mapping = getMappingByRemotePath( file_path )
            if mapping:
                file_path = mapping.getLocalPath( file_path )
        
        mapped_s += s[pos:m.start()]
        mapped_s += file_path
        pos = m.end()
        
        # mline = line_num_re.match(s[pos:])
        # if mline:
            # mapped_s += ':' + mline.group(1) + ': '
            # pos += mline.end()
    
    mapped_s += s[pos:]
    
    return mapped_s

def    _processBuildOutput( output, host_data, build_path, _errors_re = re.compile("\s+(error|warning|note):")):
    
    errors = []
    
    while True:
        s = output.readline()
        if not s:
            break
        
        s = _antPrefixFilter( s )
        s = _mapFilePaths( s, host_data, build_path )
        if _errors_re.search(s):
            if s not in errors:
              errors.append( s )
        
        sys.stdout.write( s )
        sys.stdout.flush()
    
    if errors:
        sys.stdout.write( '\n' + "#" * 64 )
        sys.stdout.write( '\n' + "#   ERRORS" )
        sys.stdout.write( '\n' + "#" * 64  + '\n')
        sys.stdout.write( ''.join( errors ) )
        sys.stdout.flush()

def     runAnt( target, build_path ):
    
    print "%"*64 + '\n' + "% TARGET: " + target + "\n" + "%"*64
    sys.stdout.flush()
    
    build_path = _findBuildXml( build_path )
    m = getMappingByLocalPath( build_path )
    if not m:
        print "Can't get a remote path from local path:", build_path
        return
        
    remote_build_path = m.getRemotePath( build_path )
    
    sim = _REMOTE_HOSTS['sim']
    
    cmd = 'cd %s; ant -Ddebug=true -Ddoc=false' % remote_build_path
    if 'remote' in target:
      cmd += ' -Dremote=%(host)s -DUserRemote=%(login)s -DPasswordRemote=%(password)s' % \
                                  { 'host':sim.host, 'login':sim.login, 'password':sim.password }
    
    cmd += ' ' + target
    
    out = m.host_data.execRemote( cmd )
    _processBuildOutput( out.stdout, m.host_data, build_path )

#//---------------------------------------------------------------------------//

def   runSchedulerTest():
    sim = _REMOTE_HOSTS['sim']
    out = sim.execRemote( 'cd /EMC/CEM/bin; chmod +x SchedulerSuite_comp_runner; ./SchedulerSuite_comp_runner' )
    _processBuildOutput( out.stdout, sim, '/EMC/CEM/bin' )

#//---------------------------------------------------------------------------//

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("\nError: Incorrect usage. Expected usage: %s <COMMAND> <FILEPATH>\n" % os.path.basename(sys.argv[0]) )
    else:
        cmd = sys.argv[1]
        
        #~ if cmd == 'copyFrom': copyRemote(sys.argv[2], copy_to = False)
        #~ elif cmd == 'copyTo': copyRemote(sys.argv[2], copy_to = True)
        if cmd == 'ant': runAnt(sys.argv[2], sys.argv[3] )
        elif cmd == 'run_test': runAnt('deploy_remote deploy_test_remote', sys.argv[2] ); runSchedulerTest()
