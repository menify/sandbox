import io
import pickle
import unittest

class AqlTests(unittest.TestCase):
  
  testcases = set()
  
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
  
  def testSaveLoad( self, value ):
    with io.BytesIO() as saved_status:
      saver = pickle.Pickler( saved_status, protocol = pickle.HIGHEST_PROTOCOL )
      saver.dump( ( value, ) )
      
      saved_status.seek(0)
      
      loader = pickle.Unpickler( saved_status )
      loaded_values = loader.load()
      loaded_value = loaded_values[0]
      
      self.assertEqual( value, loaded_value )
      self.assertEqual( value.content, loaded_value.content )
  
  #//=======================================================//
  


def  testcase( test_case ):
  if callable(test_case):
    test_case_name = test_case.__name__
    setattr( AqlTests, test_case_name, test_case )
    AqlTests.testcases.add( test_case_name )
  
  return test_case

#//===========================================================================//

def  skip( test_case ):
  if callable(test_case):
    try:
      AqlTests.testcases.remove( test_case.__name__ )
    except KeyError:
      pass
  
  return test_case

#//===========================================================================//

def runTests( settings, tests = None, add_tests = None, skip_tests = None, start_from_test = None ):
  
  if not tests:
    tests = AqlTests.testcases
  
  tests = sorted(tests)
  
  try:
    if start_from_test is not None:
      tests = tests[ tests.index( start_from_test): ]
  except ValueError:
    pass
  
  tests = set(tests)
  
  if add_tests is not None:
    tests |= set(add_tests)
  
  if skip_tests is not None:
    tests -= set(skip_tests)
  
  tests = sorted(tests)
  
  suite = unittest.TestSuite()
  for test_method in tests:
    suite.addTest( AqlTests( test_method, settings ) )
  
  unittest.TextTestRunner().run(suite)

#//===========================================================================//

