#
# Copyright (c) 2011,2012 The developers of Aqualid project - http://aqualid.googlecode.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import io
import os
import sys
import hashlib
import threading
import traceback
import inspect
import subprocess

from aql_errors import CommandExecFailed

#//===========================================================================//

def     isSequence( value, iter = iter, isinstance = isinstance, str = str ):
  try:
    if not isinstance( value, str ):
      iter( value )
      return True
  except TypeError:
    pass
  
  return False

#//===========================================================================//

def   toSequence( value, iter = iter, tuple = tuple, isinstance = isinstance, str = str ):
  
  try:
    if not isinstance( value, str ):
      iter( value )
      return value
  except TypeError:
    pass
  
  if value is None:
    return tuple()
  
  return ( value, )

#//===========================================================================//

if hasattr(os, 'O_NOINHERIT'):
  _O_NOINHERIT = os.O_NOINHERIT
else:
  _O_NOINHERIT = 0

if hasattr(os, 'O_SYNC'):
  _O_SYNC = os.O_SYNC
else:
  _O_SYNC = 0

def   openFile( filename, read = True, write = False, binary = False, sync = False, flags = _O_NOINHERIT ):
  
  mode = 'r'
  
  if not write:
    flags |= os.O_RDONLY
    sync = False
  else:
    flags |= os.O_CREAT
    mode += '+'
    
    if read:
      flags |= os.O_RDWR
    else:
      flags |= os.O_WRONLY
    
    if sync:
      flags |= _O_SYNC
    
  if binary:
    mode += 'b'
    flags |= os.O_BINARY
    
  fd = os.open( filename, flags )
  try:
    if sync:
      f = io.open( fd, mode, 0 )
    else:
      f = io.open( fd, mode )
  except:
    os.close( fd )
    raise
  
  return f

#//===========================================================================//

def readTextFile( filename ):
  with openFile( filename ) as f:
    return f.read()

def readBinFile( filename ):
  with openFile( filename, binary = True ) as f:
    return f.read()

def writeTextFile( filename, buf ):
  with openFile( filename, write = True ) as f:
    f.truncate()
    f.write( buf )

def writeBinFile( filename, buf ):
  with openFile( filename, write = True, binary = True ) as f:
    f.truncate()
    f.write( buf )

#//===========================================================================//

def   fileSignature( filename, chunk_size = hashlib.md5().block_size * (2 ** 12) ):
  
  checksum = hashlib.md5()
  
  with openFile( filename, binary = True ) as f:
    read = f.read
    checksum_update = checksum.update
    
    chunk = True
    
    while chunk:
      chunk = read( chunk_size )
      checksum_update( chunk )
  
  return checksum.digest()

#//===========================================================================//

def   fileChecksum( filename, offset = 0, size = -1, alg = 'md5', chunk_size = 262144 ):
  
  checksum = hashlib.__dict__[alg]()
  
  with openFile( filename, binary = True ) as f:
    read = f.read
    f.seek( offset )
    checksum_update = checksum.update
    
    chunk = True
    
    while chunk:
      chunk = read( chunk_size )
      checksum_update( chunk )
      
      if size > 0:
        size -= len(chunk)
        if size <= 0:
          break
      
      checksum_update( chunk )
  
  return checksum

#//===========================================================================//

def   getFunctionName( currentframe = inspect.currentframe ):
  
  frame = currentframe()
  if frame:
    return frame.f_back.f_code.co_name
  
  return "__not_avaiable__"
  
  #~ try:
    #~ raise Exception()
  #~ except Exception as err:
    #~ return err.__traceback__.tb_frame.f_back.f_code.co_name

#//===========================================================================//

def   printStacks():
  id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
  
  for thread_id, stack in sys._current_frames().items():
    print("\n" + ("=" * 64) )
    print("Thread: %s (%s)" % (id2name.get(thread_id,""), thread_id))
    traceback.print_stack(stack)


#//===========================================================================//

try:
  _getargspec = inspect.getfullargspec
except AttributeError:
  _getargspec = inspect.getargspec

#//===========================================================================//

def   equalFunctionArgs( function1, function2, getargspec = _getargspec):
  if id(function1) == id(function2):
    return True
  
  return getargspec( function1 )[0:3] == getargspec( function2 )[0:3]

#//===========================================================================//

def   checkFunctionArgs( function, args, kw, getargspec = _getargspec):
  
  f_args, f_varargs, f_varkw, f_defaults = getargspec( function )[:4]
  
  current_args_num = len(args) + len(kw)
  
  args_num = len(f_args)
  
  if not f_varargs and not f_varkw:
    if current_args_num > args_num:
      return False
  
  if f_defaults:
    def_args_num = len(f_defaults)
  else:
    def_args_num = 0
  
  min_args_num = args_num - def_args_num
  if current_args_num < min_args_num:
    return False
  
  kw = set(kw)
  unknown_args = kw - set(f_args)
  
  if unknown_args and not f_varkw:
    return False
  
  def_args = f_args[args_num - def_args_num:]
  non_def_kw = kw - set(def_args)
  
  non_def_args_num = len(args) + len(non_def_kw)
  if non_def_args_num < min_args_num:
    return False
  
  twice_args = set(f_args[:len(args)]) & kw
  if twice_args:
    return False
  
  return True

#//===========================================================================//

def  findFiles( path = ".", prefix = "", suffix = "", ignore_dir_prefixes = ('__', '.') ):
  
  found_files = []
  
  ignore_dir_prefixes = toSequence(ignore_dir_prefixes)
  
  for root, dirs, files in os.walk( path ):
    for file_name in files:
      file_name = file_name.lower()
      if file_name.startswith( prefix ) and file_name.endswith( suffix ):
        found_files.append( os.path.join(root, file_name))
    
    tmp_dirs = []
    
    for dir in dirs:
      for dir_prefix in ignore_dir_prefixes:
        if not dir.startswith( dir_prefix ):
          tmp_dirs.append( dir )
    
    dirs[:] = tmp_dirs
  
  return found_files

#//===========================================================================//

def _decodeData( data ):
  if not data:
    return str()
  
  try:
    codec = sys.stdout.encoding
  except AttributeError:
    codec = None
  
  if not codec:
    codec = 'utf_8'
  
  if not isinstance(data, str):
    data = data.decode( codec )
  
  return data

#//===========================================================================//

def execCommand( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = None, env = None ):
  try:
    # print( "execCommand: %s" % cmd )
    p = subprocess.Popen( cmd, stdout = stdout, stderr = stderr, cwd = cwd, env = env )
    (stdoutdata, stderrdata) = p.communicate()
    result = p.returncode
  except Exception as ex:
    raise CommandExecFailed( str(ex) + ': ' + cmd )
  
  stdoutdata = _decodeData( stdoutdata )
  stderrdata = _decodeData( stderrdata )

  return result, stdoutdata, stderrdata
