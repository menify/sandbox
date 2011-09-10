import re
import imp
import sys
import os.path


sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', 'utils') )
sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', 'values') )

from aql_tests import runTests
from aql_logging import logInfo

#//===========================================================================//

def  _findTestModules():
  test_case_re = re.compile(r"^aql_test_.+\.py$")
  
  test_case_modules = []
  
  for root, dirs, files in os.walk( os.path.dirname( __file__ ) ):
    for file_name in files:
      if test_case_re.match( file_name ):
        test_case_modules.append( os.path.join(root, file_name))
    dirs[:] = filter( lambda d: not d.startswith('.') or d.startswith('__'), dirs )
  
  return test_case_modules

#//===========================================================================//

def   _loadTestModules( test_modules ):
  
  for module_file in test_modules:
    
    module_dir = os.path.dirname( module_file )
    module_name = os.path.splitext( os.path.basename( module_file) )[0]
    
    fp, pathname, description = imp.find_module( module_name, [ module_dir ] )
    
    with fp:
      user_mod = imp.load_module( module_name, fp, pathname, description )
      
      logInfo( "Loaded module: %s", user_mod.__file__ )

#//===========================================================================//

def   _importTestModules():
  _loadTestModules( _findTestModules() )

#//===========================================================================//

def  _getExecTests( tests ):
  
  exec_tests = set()
  add_tests = set()
  skipp_tests = set()
  start_from_test = None
  
  for test in tests:
    if test.startswith('+'):
      add_tests.add( test[1:] )
    
    elif test.startswith('-'):
      skip_tests.add( test[1:] )
    
    elif test.startswith('~'):
      start_from_test = test[1:]
    
    elif test:
      exec_tests.add( test )
  
  return (exec_tests, add_tests, skipp_tests, start_from_test)

#//===========================================================================//


class _Settings( object ):
  def   __init__(self):
    from optparse import OptionParser
    
    parser = OptionParser()
    
    parser.add_option("-c", "--config", dest = "config",
                      help = "Path to config file", metavar = "FILE PATH")
    
    parser.add_option("-x", "--tests", dest = "tests",
                      help = "List of tests which should be executed", metavar = "TESTS")
    
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose",
                      help = "Quiet mode", default = True )
    
    (options, args) = parser.parse_args()
    print_usage = False
    
    settings = {}
    
    if options.config is not None:
      if not os.path.isfile(options.config):
        print( "Error: Config file doesn't exist." )
        print_usage = True
      else:
        execfile( options.config, {}, settings )
    
    for opt,value in options.__dict__.items():
      if (value is not None) or (opt not in settings):
        settings[ opt ] = value
    
    tests = settings['tests']
    if tests is None:
      settings['tests'] = []
    else:
      if not isinstance( tests, (list, tuple) ):
        settings['tests'] = tests.split(',')
    
    self.__dict__ = settings

#//===========================================================================//
#//===========================================================================//

if __name__ == "__main__":
  
  _importTestModules()
  
  settings = _Settings()
  
  exec_tests, add_tests, skipp_tests, start_from_test = _getExecTests( settings.tests )
  
  #//-------------------------------------------------------//
  
  runTests( settings, exec_tests, add_tests, skipp_tests, start_from_test )

