import os
import time
import errno

#//===========================================================================//
#   General implementation
#//===========================================================================//
class GeneralFileLock (object):
  
  class Timeout( Exception ): pass
  
  __slots__ = ('lockfilename', 'fd', 'retries', 'interval')
  
  def   __init__( self, filename, interval = 1, timeout = 3 * 60):
    self.lockfilename = os.path.normcase( os.path.normpath( os.path.abspath( str(filename) ) ) ) + '.lock'
    self.fd = None
    self.interval = interval
    self.retries = int(timeout / interval)
  
  def   __del__(self):
    self.releaseLock()
  
  def   __enter__(self):
    return self

  def   __exit__(self, exc_type, exc_value, traceback):
    self.releaseLock()
  
  def   readLock( self ):
    return self.writeLock()
  
  def   writeLock( self, os_open = os.open, open_flags = os.O_CREAT| os.O_EXCL | os.O_RDWR ):
    if self.fd is not None:
      return self
      
    index = self.retries
    
    while True:
      try:
        self.fd = os_open( self.lockfilename, open_flags )
        break
      except OSError as ex:
        self.fd = None
        if ex.errno != errno.EEXIST:
          raise
        if not index:
            raise self.Timeout("Lock file '%s' timeout." % self.lockfilename )
        
        index -= 1
        
      time.sleep( self.interval )
    
    return self
  
  def   releaseLock( self, close = os.close, remove = os.remove ):
    if self.fd is not None:
      close(self.fd)
      remove(self.lockfilename)
      self.fd = None


try:
  #//===========================================================================//
  #   Unix implementation
  #//===========================================================================//
  import fcntl
  
  class UnixFileLock (object):
    
    __slots__ = ('fd')
  
    def   __init__( self, filename ):
      self.fd = os.open( filename, os.O_RDWR | os.O_CREAT )
    
    def   __del__(self):
      os.close( self.fd )
    
    def   __enter__(self):
      return self
  
    def   __exit__(self, exc_type, exc_value, traceback):
      self.releaseLock()
    
    def   readLock( self, lockf = fcntl.lockf, LOCK_SH = fcntl.LOCK_SH ):
      lockf( self.fd, LOCK_SH )
      return self
    
    def   writeLock( self, lockf = fcntl.lockf, LOCK_EX = fcntl.LOCK_EX):
      lockf( self.fd, LOCK_EX )
      return self
    
    def   releaseLock( self, lockf = fcntl.lockf, LOCK_UN = fcntl.LOCK_UN):
      lockf( self.fd, LOCK_UN )
  
  FileLock = UnixFileLock
  
except ImportError:

  try:
    #//===========================================================================//
    #   Widows implementation
    #//===========================================================================//
    import win32con
    import win32file
    import pywintypes
    
    class WindowsFileLock (object):
      
      __slots__ = ('hfile', 'locked')
      _overlapped = pywintypes.OVERLAPPED()
    
      def   __init__( self, filename ):
        lockfilename = filename + ".lock"
        
        self.hfile = win32file.CreateFile( lockfilename,
                                           win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                           win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
                                           None,
                                           win32file.OPEN_ALWAYS,
                                           0,
                                           None )
        self.locked = False
      
      def   __del__(self):
        self.hfile.Close()
      
      def   __enter__(self):
        return self
    
      def   __exit__(self, exc_type, exc_value, traceback):
        self.releaseLock()
      
      def   readLock( self, LockFileEx = win32file.LockFileEx, overlapped = _overlapped ):
        LockFileEx( self.hfile, 0, 0, 4096, overlapped )
        self.locked = True
        return self
      
      def   writeLock( self, LockFileEx = win32file.LockFileEx, LOCKFILE_EXCLUSIVE_LOCK = win32con.LOCKFILE_EXCLUSIVE_LOCK, overlapped = _overlapped):
        LockFileEx( self.hfile, LOCKFILE_EXCLUSIVE_LOCK, 0, 4096, overlapped )
        self.locked = True
        return self
      
      def   releaseLock( self, UnlockFileEx = win32file.UnlockFileEx, overlapped = _overlapped ):
        if self.locked:
          UnlockFileEx( self.hfile, 0, 4096, overlapped )
          self.locked = False
    
    FileLock = WindowsFileLock
    
  except ImportError:
    
    FileLock = GeneralFileLock