import io
import sys
import time
import pickle
import os.path
import tempfile
import unittest

sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', '..', 'utils') )
sys.path.insert( 0, os.path.join( os.path.dirname( __file__ ), '..', '..', 'values') )

from aql_temp_file import Tempfile
from aql_logging import logDebug, logError
from aql_file_value import FileValue, FileName, FileContentChecksum, FileContentTimeStamp

#//===========================================================================//
def _listAllTests( TestCasesClass ):
  tests = []
  for name, instance in TestCasesClass.__dict__.items():
    if callable(instance) and name.startswith('test'):
      tests.append( name )
  
  return tests

#//===========================================================================//

def  _filterTests( tests, TestCasesClass ):
  
  exec_tests = set()
  append_tests = set()
  remove_tests = set()
  start_from_test = None
  
  for test in tests:
    if test.startswith('+'):
      append_tests.add( test[1:] )
    
    elif test.startswith('-'):
      remove_tests.add( test[1:] )
    
    elif test.startswith('~'):
      start_from_test = test[1:]
    
    elif test:
      exec_tests.add( test )
  
  if not exec_tests:
    exec_tests = _listAllTests( TestCasesClass )
  
  exec_tests = sorted(exec_tests)
  
  try:
    if start_from_test is not None:
      exec_tests = exec_tests[ exec_tests.index( start_from_test): ]
  except ValueError:
    pass
  
  exec_tests = set(exec_tests)
  
  exec_tests |= append_tests
  exec_tests -= remove_tests
  
  return sorted(exec_tests)

#//===========================================================================//


class _GlobalSettings( object ):
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


class AqlTests(unittest.TestCase):
  
  def   __init__(self, testname, settings ):
    super(AqlTests, self).__init__(testname)
    
    self.settings = settings
    self.result = self.defaultTestResult()
  
  #//=======================================================//
  
  def run( self, result = None ):
    if result is not None:
      self.result = result
    
    super( AqlTests, self ).run( self.result )
  
  #//=======================================================//
  
  def   tearDown(self):
    if not self.result.wasSuccessful():
      self.result.stop()
    
  #//===========================================================================//
  
  def   setUp(self):
    if not self.result.wasSuccessful():
      self.result.stop()
    
    print("")
    print( "*" * 64)
    print("* TestCase:", self.id())
    print("*" * 64)
  
  #//=======================================================//
  
  def test_temp_file(self):
    temp_file_name = None
    
    with Tempfile() as temp_file:
      
      temp_file.write( '1234567890\n1234567890'.encode() )
      temp_file.flush()
      
      temp_file_name = temp_file.name
    
    self.assertFalse( os.path.isfile(temp_file_name) )
    
  #//=======================================================//
  
  def test_temp_file_rw(self):
    temp_file_name = None
    
    with Tempfile() as temp_file:
      
      test_string = '1234567890'
      
      temp_file.write( test_string.encode() )
      temp_file.flush()
      
      temp_file_name = temp_file.name
      
      with open(temp_file_name, "r") as temp_file_rh:
        test_string_read = temp_file_rh.read()
        self.assertEqual( test_string,test_string_read )
    
  #//=======================================================//
  
  def test_file_value(self):
    with Tempfile() as temp_file:
      test_string = '1234567890'
      
      temp_file.write( test_string.encode() )
      temp_file.flush()

      temp_file_value1 = FileValue( temp_file.name )
      temp_file_value2 = FileValue( temp_file.name )
      
      self.assertEqual( temp_file_value1, temp_file_value2 )
      self.assertEqual( temp_file_value1.content, temp_file_value2.content )
      
      reversed_test_string = str(reversed(test_string))
      temp_file.seek( 0 )
      temp_file.write( reversed_test_string.encode() )
      temp_file.flush()
      
      temp_file_value2 = FileValue( temp_file_value1 )
      self.assertEqual( temp_file_value1, temp_file_value2 )
      self.assertNotEqual( temp_file_value1.content, temp_file_value2.content )

  #//=======================================================//
  
  def test_file_value_save_load(self):
    
    temp_file_name = None
    
    with Tempfile() as temp_file:
      test_string = '1234567890'
      
      temp_file.write( test_string.encode() )
      temp_file.flush()
      
      temp_file_name = temp_file.name
      
      temp_file_value = FileValue( temp_file_name )
      
    with io.BytesIO() as saved_status:
      saver = pickle.Pickler( saved_status, protocol = pickle.HIGHEST_PROTOCOL )
      saver.dump( ( temp_file_value, ) )
      
      saved_status.seek(0)
      
      loader = pickle.Unpickler( saved_status )
      loaded_values = loader.load()
      loaded_file_value = loaded_values[0]
      
      self.assertEqual( temp_file_value, loaded_file_value )
      self.assertEqual( temp_file_value.content, loaded_file_value.content )
    
    temp_file_value = FileValue( temp_file_name )
    self.assertEqual( temp_file_value, loaded_file_value )
    self.assertNotEqual( temp_file_value.content, loaded_file_value.content )
    self.assertFalse( temp_file_value.exists() )
  
  #//=======================================================//
  
  def test_file_value_time(self):
    with Tempfile() as temp_file:
      test_string = '1234567890'
      
      temp_file.write( test_string.encode() )
      temp_file.flush()

      temp_file_value1 = FileValue( temp_file.name, FileContentTimeStamp )
      temp_file_value2 = FileValue( temp_file.name, FileContentTimeStamp )
      
      self.assertEqual( temp_file_value1, temp_file_value2 )
      self.assertEqual( temp_file_value1.content, temp_file_value2.content )
      
      time.sleep(1)
      temp_file.seek( 0 )
      temp_file.write( test_string.encode() )
      temp_file.flush()
      
      temp_file_value2 = FileValue( temp_file_value1, FileContentTimeStamp )
      self.assertEqual( temp_file_value1, temp_file_value2 )
      self.assertNotEqual( temp_file_value1.content, temp_file_value2.content )

  #//=======================================================//
  
  def test_file_value_time_save_load(self):
    
    temp_file_name = None
    
    with Tempfile() as temp_file:
      test_string = '1234567890'
      
      temp_file.write( test_string.encode() )
      temp_file.flush()
      
      temp_file_name = temp_file.name
      
      temp_file_value = FileValue( temp_file_name, FileContentTimeStamp )
      
    with io.BytesIO() as saved_status:
      saver = pickle.Pickler( saved_status, protocol = pickle.HIGHEST_PROTOCOL )
      saver.dump( ( temp_file_value, ) )
      
      saved_status.seek(0)
      
      loader = pickle.Unpickler( saved_status )
      loaded_values = loader.load()
      loaded_file_value = loaded_values[0]
      
      self.assertEqual( temp_file_value, loaded_file_value )
      self.assertEqual( temp_file_value.content, loaded_file_value.content )
    
    temp_file_value = FileValue( temp_file_name, FileContentTimeStamp )
    self.assertEqual( temp_file_value, loaded_file_value )
    self.assertNotEqual( temp_file_value.content, loaded_file_value.content )
    self.assertFalse( temp_file_value.exists() )

#//===========================================================================//
#//===========================================================================//

if __name__ == "__main__":
  
  settings = _GlobalSettings()
  
  tests = _filterTests( settings.tests, AqlTests )
  
  #//-------------------------------------------------------//
  
  suite = unittest.TestSuite()
  for test_method in tests:
    suite.addTest( AqlTests( test_method, settings ) )
  
  #//-------------------------------------------------------//
  
  unittest.TextTestRunner().run(suite)

