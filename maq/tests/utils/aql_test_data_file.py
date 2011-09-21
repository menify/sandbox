
from aql_tests import testcase, skip
from aql_temp_file import Tempfile
from aql_data_file import DataFile

#//===========================================================================//

@testcase
def test_data_file(self):
  tmp = Tempfile()
  tmp.remove()
  
  df = DataFile( tmp.name )
  
  
  
#//===========================================================================//
