import os

class _LockHolder (object):
  
  __slots__ = ('lock')
  
  def   __init__( self, lock ):
    self.lock = lock
  
  def   __enter__(self):
    return self
  
  def   __exit__(self, exc_type, exc_value, traceback):
    self.lock.releaseLock()

try:
  #//===========================================================================//
  #   Unix implementation
  #//===========================================================================//
  import fcntl
  
  class FileLock (object):
    
    __slots__ = ('fd')
  
    def   __init__( self, filename ):
      self.fd = os.open( filename, os.O_RDWR | os.O_CREAT )
    
    def   __del__(self):
      os.close( self.fd )
    
    def   acquireReadLock( self, lockf = fcntl.lockf, LOCK_SH = fcntl.LOCK_SH ):
      lockf( self.fd, LOCK_SH )
      
      return _LockHolder( self )
    
    def   acquireWriteLock( self, lockf = fcntl.lockf, LOCK_EX = fcntl.LOCK_EX):
      lockf( self.fd, LOCK_EX )
      
      return _LockHolder( self )
    
    def   releaseLock( self, lockf = fcntl.lockf, LOCK_UN = fcntl.LOCK_UN):
      lockf( self.fd, LOCK_UN )
  
except ImportError:

  try
    #//===========================================================================//
    #   Widows implementation
    #//===========================================================================//
    import win32con
    import win32file
    import pywintypes
    
    _overlapped = pywintypes.OVERLAPPED()
    
    class FileLock (object):
      
      __slots__ = ('fd', 'hfile')
    
      def   __init__( self, filename ):
        lockfilename = filename + ".lock"
        
        fd = os.open( lockfilename, os.O_RDWR | os.O_CREAT )
        self.fd =fd
        self.hfile = win32file._get_osfhandle( fd )
      
      def   __del__(self):
        os.close( self.fd )
      
      def   acquireReadLock( self, LockFileEx = win32file.LockFileEx, overlapped = _overlapped ):
        LockFileEx( self.hfile, 0, 0, 4096, overlapped )
        
        return _LockHolder( self )
      
      def   acquireWriteLock( self, LockFileEx = win32file.LockFileEx, LOCKFILE_EXCLUSIVE_LOCK = win32con.LOCKFILE_EXCLUSIVE_LOCK, overlapped = _overlapped):
        LockFileEx( self.hfile, LOCKFILE_EXCLUSIVE_LOCK, 0, 4096, overlapped )
        
        return _LockHolder( self )
      
      def   releaseLock( self, LockFileEx = win32file.UnlockFileEx, overlapped = _overlapped):
        UnlockFileEx( self.hfile, 0, 4096, overlapped )
  
  except ImportError:
    
    import time
    import errno
    
    #//===========================================================================//
    #   Common implementation
    #//===========================================================================//
    class FileLock (object):
      
      __slots__ = ('lockfilename', 'fd')
      
      __TIMEOUT = 2 * 60
      __DELAY = 1
    
      def   __init__( self, filename ):
        self.lockfilename = os.path.normcase( os.path.normpath( os.path.abspath( str(filename) ) ) ) + '.lock'
        self.fd = None
      
      def   __del__(self):
        self.releaseLock()
      
      def   acquireReadLock( self ):
        return self.acquireWriteLock()
      
      def   acquireWriteLock( self, open = os.open, open_flags = os.O_CREAT| os.O_EXCL | os.O_RDWR, clock = time.clock ):
        
        start_time = clock()
        
        while True:
          try:
            self.fd = open( self.lockfilename, open_flags )
            break
          except OSError as e:
            self.fd = None
            if (e.errno != errno.EEXIST) or \
               ((clock() - start_time) >= self.__TIMEOUT):
                raise
          
          time.sleep( self.__DELAY )
        
        return _LockHolder( self )
      
      def   releaseLock( self, close = os.close, remove = os.remove ):
        if self.fd is not None:
          self.fd = None
          close(self.fd)
          remove(self.lockfilename)
