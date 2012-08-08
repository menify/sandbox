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


import re
import os.path

#//===========================================================================//
#//===========================================================================//

class   IgnoreCaseString (str):

  def     __new__(cls, value = None ):
    
    if (cls is IgnoreCaseString) and (type(value) is cls):
        return value
    
    if value is None:
        value = ''
    else:
        value = str(value)
    
    self = super(IgnoreCaseString, cls).__new__(cls, value)
    self.__value = value.lower()
    
    return self
  
  #//-------------------------------------------------------//
  
  def   __hash__(self):
    return hash(self.__value)
  
  def   __eq__( self, other):
    return self.__value == IgnoreCaseString( other ).__value
  def   __ne__( self, other):
    return self.__value != IgnoreCaseString( other ).__value
  def   __lt__( self, other):
    return self.__value <  IgnoreCaseString( other ).__value
  def   __le__( self, other):
    return self.__value <= IgnoreCaseString( other ).__value
  def   __gt__( self, other):
    return self.__value >  IgnoreCaseString( other ).__value
  def   __ge__( self, other):
    return self.__value >= IgnoreCaseString( other ).__value

#//===========================================================================//
#//===========================================================================//

class   LowerCaseString (str):

  def     __new__(cls, value = None ):
    
    if (cls is LowerCaseString) and (type(value) is cls):
        return value
    
    if value is None:
        value = ''
    else:
        value = str(value)
    
    return super(LowerCaseString, cls).__new__(cls, value.lower())

#//===========================================================================//
#//===========================================================================//

class   UpperCaseString (str):

  def     __new__(cls, value = None ):
    
    if (cls is UpperCaseString) and (type(value) is cls):
        return value
    
    if value is None:
        value = ''
    else:
        value = str(value)
    
    return super(UpperCaseString, cls).__new__(cls, value.upper())

#//===========================================================================//
#//===========================================================================//

class   Version (str):

  __ver_re = re.compile(r'[0-9]+[a-zA-Z]*(\.[0-9]+[a-zA-Z]*)*')
  
  def     __new__(cls, version = None, _ver_re = __ver_re ):
    
    if (cls is Version) and (type(version) is cls):
        return version
    
    if version is None:
        ver_str = ''
    else:
        ver_str = str(version)
    
    match = _ver_re.search( ver_str )
    if match:
        ver_str = match.group()
        ver_list = re.findall(r'[0-9]+|[a-zA-Z]+', ver_str )
    else:
        ver_str = ''
        ver_list = []
    
    self = super(Version, cls).__new__(cls, ver_str )
    conv_ver_list = []
    
    for v in ver_list:
        if v.isdigit():
            v = int(v)
        conv_ver_list.append( v )
    
    self.__version = tuple(conv_ver_list)
    
    return self
  
  #//-------------------------------------------------------//
  
  def   __hash__(self):
    return hash(self.__version)
  
  def   __eq__( self, other):
    return self.__version == Version( other ).__version
  def   __lt__( self, other):
    return self.__version <  Version( other ).__version
  def   __le__( self, other):
    return self.__version <= Version( other ).__version
  def   __ne__( self, other):
    return self.__version != Version( other ).__version
  def   __gt__( self, other):
    return self.__version >  Version( other ).__version
  def   __ge__( self, other):
    return self.__version >= Version( other ).__version

#//===========================================================================//

if os.path.normcase('ABC') == os.path.normcase('abc'):
  FilePathBase = IgnoreCaseString
else:
  FilePathBase = str

class   FilePath (FilePathBase):
  
  #//-------------------------------------------------------//
  
  def     __new__(cls, path = None ):
    if (cls is FilePath) and (type(path) is cls):
      return path
    
    if path is None:
        path = ''
    
    path = os.path.normpath( str(path) )
    
    return super(FilePath,cls).__new__( cls, path )
  
  #//-------------------------------------------------------//
  
  def   __eq__( self, other ):
    return super(FilePath,self).__eq__( FilePath( other ) )
  def   __ne__( self, other ):
    return super(FilePath,self).__ne__( FilePath( other ) )
  def   __lt__( self, other ):
    return super(FilePath,self).__lt__( FilePath( other ) )
  def   __le__( self, other ):
    return super(FilePath,self).__le__( FilePath( other ) )
  def   __gt__( self, other ):
    return super(FilePath,self).__gt__( FilePath( other ) )
  def   __ge__( self, other ):
    return super(FilePath,self).__ge__( FilePath( other ) )

#//===========================================================================//

class   FileAbsPath (FilePathBase):
  
  def     __new__(cls, path = None ):
    if (cls is FileAbsPath) and (type(path) is cls):
      return path
    
    if path is None:
        path = ''
    
    path = os.path.abspath( str(path) )
    
    return super(FileAbsPath,cls).__new__( cls, path )
  
  #//-------------------------------------------------------//
  
  def   __eq__( self, other ):
    return super(FileAbsPath,self).__eq__( FileAbsPath( other ) )
  def   __ne__( self, other ):
    return super(FileAbsPath,self).__ne__( FileAbsPath( other ) )
  def   __lt__( self, other ):
    return super(FileAbsPath,self).__lt__( FileAbsPath( other ) )
  def   __le__( self, other ):
    return super(FileAbsPath,self).__le__( FileAbsPath( other ) )
  def   __gt__( self, other ):
    return super(FileAbsPath,self).__gt__( FileAbsPath( other ) )
  def   __ge__( self, other ):
    return super(FileAbsPath,self).__ge__( FileAbsPath( other ) )

