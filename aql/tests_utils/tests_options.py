﻿import os.path
import optparse

__all__ = ( 'TestsOptions', )

try:
  unicode("test")
except NameError:
  unicode = str

def   _toSequence( value ):
  if value is None:
    return None
  
  try:
    if isinstance( value, (str, unicode) ):
      return value.split(',')
    else:
      iter( value )
      return value
  except TypeError:
    pass
  
  return ( value, )

#//===========================================================================//

def   _toBool( value ):
  if isinstance( value, (str, unicode) ):
    return value.lower() == 'true'
  
  return bool( value )

#//===========================================================================//

class TestsOptions( object ):
  
  _instance = None
  
  def   __new__( cls, configs = None, **kw):
    
    if TestsOptions._instance is not None:
      return TestsOptions._instance
    
    self = super(TestsOptions,cls).__new__(cls)
    TestsOptions._instance = self
    
    opt, args = self.__getOptArgs()
    
    self.setOption( 'test_modules_prefix',  opt.test_modules_prefix,        'test_' )
    self.setOption( 'test_methods_prefix',  opt.test_methods_prefix,        'test'  )
    self.setOption( 'verbose',              opt.verbose,                    False   )
    self.setOption( 'keep_going',           opt.keep_going,                 False   )
    self.setOption( 'reset',                opt.reset,                      False   )
    self.setOption( 'list_tests',           opt.list_tests,                 False   )
    self.setOption( 'tests_dirs',           _toSequence( opt.tests_dirs ),  '.'     )
    
    self.__parseTests( opt.tests )
    self.__parseArguments( args )
    
    for name,value in kw.items():
      self.setOption( name, value )
    
    self.appyConfig( opt.configs )
    self.appyConfig( configs )
    
    self.normalizeKnownOptions()
    
    return self
  
  #//=======================================================//
  
  @staticmethod
  def   __getOptArgs():
    parser = optparse.OptionParser("usage: %prog [OPTIONS] [ARGUMENT=VALUE ...]")
    
    parser.add_option("-d", "--dir", dest = "tests_dirs",
                      help = "Tests directory", metavar = "DIR PATH,..." )
    
    parser.add_option("-p", "--prefix", dest = "test_modules_prefix",
                      help = "File name prefix of test modules", metavar = "FILE PATH PREFIX" )
    
    parser.add_option("-m", "--method-prefix", dest = "test_methods_prefix",
                      help = "Test methods prefix", metavar = "TEST METHOD PREFIX" )
    
    parser.add_option("-c", "--config", dest = "configs",
                      help = "Path to config file(s).", metavar = "FILE PATH,...")
    
    parser.add_option("-x", "--tests", dest = "tests",
                      help = "Comma separated list of tests which should be executed.", metavar = "[+-~]TEST,...")
    
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help = "Verbose mode." )
    
    parser.add_option("-k", "--keep-going", action="store_true", dest="keep_going",
                      help = "Keep going even if any test case failed." )
    
    parser.add_option("-r", "--reset", action="store_true", dest = "reset",
                      help = "Reset configuration" )
    
    parser.add_option("-l", "--list", action="store_true", dest="list_tests",
                      help = "List test cases and exit." )
    
    opt, args = parser.parse_args()
    
    return (opt, args)

  #//=======================================================//

  def   __parseArguments( self, args ):
    for arg in args:
      name, sep, value = arg.partition('=')
      if not sep:
        raise Exception("Error: Invalid commmand line argument.")
      
      self.setOption( name.strip(), value.strip() )
  
  #//=======================================================//
  
  def  __parseTests( self, tests ):
    
    if tests is not None:
      tests = _toSequence( tests )
    else:
      tests = ()
    
    run_tests = None
    add_tests = set()
    skip_tests = set()
    start_from_tests = set()
    
    for test in tests:
      test = test.strip()
      if test.startswith('+'):
        add_tests.add( test[1:] )
      
      elif test.startswith('-'):
        skip_tests.add( test[1:] )
      
      elif test.startswith('~'):
        start_from_tests.add( test[1:] )
      
      elif test:
        if run_tests is None:
          run_tests = set()
        run_tests.add( test )
    
    self.setOption( 'run_tests', run_tests )
    self.setOption( 'add_tests', add_tests )
    self.setOption( 'skip_tests', skip_tests )
    self.setOption( 'start_from_tests', start_from_tests )

  #//=======================================================//
  
  def   appyConfig( self, config ):
    if config is None:
      return
    
    for config in _toSequence( config ):
      if not os.path.isfile(config):
        raise Exception( "Error: Config file doesn't exist." )
      
      settings = {}
      execfile( config, {}, settings )
      
      for key,value in settings.items():
        self.setOption( key, value )
  
  #//=======================================================//
  
  def   setOption( self, name, value, default_value = None ):
    
    options = self.__dict__.setdefault('__options', {} )
    
    current_value = options.get( name, None )
    
    if current_value is None:
      if value is not None:
        options[ name ] = value
        setattr( self, name, value )
      
      elif default_value is not None:
        setattr( self, name, default_value )
  
  #//=======================================================//
  
  def   setDefault( self, name, default_value ):
    options = self.__dict__.setdefault('__options', {} )
    current_value = options.get( name, None )
    if current_value is None:
      setattr( self, name, default_value )
  
  #//=======================================================//
  
  def  __normOption( self, name, normalizer ):
    try:
      setattr( self, name, normalizer(getattr( self, name )) )
    except AttributeError:
      pass
  
  #//=======================================================//
  
  def   normalizeKnownOptions( self ):
    self.__normOption( 'test_modules_prefix', str )
    self.__normOption( 'test_methods_prefix', str )
    self.__normOption( 'verbose',             _toBool )
    self.__normOption( 'list_tests',          _toBool )
    self.__normOption( 'reset',               _toBool )
    self.__normOption( 'keep_going',          _toBool )
    self.__normOption( 'tests_dirs',          _toSequence )
    self.__normOption( 'run_tests',           _toSequence )
    self.__normOption( 'add_tests',           _toSequence )
    self.__normOption( 'skip_tests',          _toSequence )
    self.__normOption( 'start_from_tests',    _toSequence )
  
  #//=======================================================//
  
  def   __getattr__(self, name ):
    return None

#//===========================================================================//

if __name__ == "__main__":
  import pprint
  pprint.pprint( TestsOptions().__dict__ )
  

