#
# Copyright (c) 2012 The developers of Aqualid project - http://aqualid.googlecode.com
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

__all__ = ( 'DictItem', 'Dict', 'ValueDictType', 'SplitDictType' )

from .aql_simple_types import castStr, isString
from .aql_list_types import List

#//===========================================================================//

class DictItem( tuple ):

  #noinspection PyInitNewSignature
  def   __new__( cls, key, value ):
    return super(DictItem, cls).__new__( cls, (key, value ) )

#//===========================================================================//

class   Dict (dict):
  
  #//-------------------------------------------------------//
  
  @staticmethod
  def   toItems( items ):
    if not items or (items is NotImplemented):
      return tuple()
    
    if isinstance( items, DictItem ):
      return (items,)
    
    try:
      items = items.items
    except AttributeError:
      return items
    
    return items()
  
  #//-------------------------------------------------------//
  
  def   __init__( self, items = None ):
    super( Dict, self).__init__( self.toItems( items ) )
  
  #//-------------------------------------------------------//
  
  def   __iadd__( self, items ):
    for key, value in self.toItems( items ):
      try:
        self[key] += value
      except KeyError:
        self[key] = value
    
    return self
  
  #//-------------------------------------------------------//
  
  def   __eq__( self, other ):
    if isinstance( other, DictItem ): return self[ other[0] ] == other[1]
    return super(Dict,self).__eq__( other )
  
  def   __lt__( self, other ):
    if isinstance( other, DictItem ): return self[ other[0] ] < other[1]
    return super(Dict,self).__lt__( other )
  
  def   __gt__( self, other ):
    if isinstance( other, DictItem ): return self[ other[0] ] > other[1]
    return super(Dict,self).__gt__( other )
  
  def   __ne__( self, other ):
    return not (self == other)
  
  def   __le__( self, other ):
    return not (self > other)
  
  def   __ge__( self, other ):
    return not (self < other)
  
  #//-------------------------------------------------------//
  
  def   dump( self ):
    return { castStr(key): castStr(value) for key, value in self.items() }
  
  #//-------------------------------------------------------//
  
  def   copy( self, key_type = None, value_type = None ):
    
    other = Dict()
    
    for key, value in self.items():
      if key_type:    key = key_type( key )
      if value_type:  value = value_type( value )
      other[ key ] = value
    
    return other

#//===========================================================================//

def   SplitDictType( dict_type, separators ):
  
  separator = separators[0]
  other_separators = separators[1:]
  
  class   SplitDict (dict_type):
    
    #//-------------------------------------------------------//
    
    @staticmethod
    def   __toItems( items_str, sep = separator, other_seps = other_separators ):
      
      if not isString( items_str ):
        return items_str
      
      for s in other_seps:
        items_str = items_str.replace( s, sep )

      items = []
      
      for v in filter( None, items_str.split( sep ) ):
        key, sep, value = v.partition('=')
        items.append( (key, value) )

      return items
    
    #//-------------------------------------------------------//
    
    @staticmethod
    def   __toSplitDict( items ):
      if isinstance( items, (SplitDict, DictItem) ):
        return items
      
      return SplitDict( items )
    
    #//-------------------------------------------------------//
    
    def     __init__( self, items = None ):
      super(SplitDict,self).__init__( self.__toItems( items ) )
    
    #//-------------------------------------------------------//
    
    def   __iadd__( self, items ):
      return super(SplitDict,self).__iadd__( self.__toItems( items ) )
    
    #//-------------------------------------------------------//
    
    def update(self, other = None, **kwargs):
      
      other = self.__toItems( other )
      
      super(SplitDict,self).update( other )
      
      items = self.__toItems( kwargs )
      
      super(SplitDict,self).update( items )
    
    #//-------------------------------------------------------//
    
    def   __eq__( self, other ):
      return super(SplitDict,self).__eq__( self.__toSplitDict( other ) )
    def   __ne__( self, other ):
      return super(SplitDict,self).__ne__( self.__toSplitDict( other ) )
    def   __lt__( self, other ):
      return super(SplitDict,self).__lt__( self.__toSplitDict( other ) )
    def   __le__( self, other ):
      return super(SplitDict,self).__le__( self.__toSplitDict( other ) )
    def   __gt__( self, other ):
      return super(SplitDict,self).__gt__( self.__toSplitDict( other ) )
    def   __ge__( self, other ):
      return super(SplitDict,self).__ge__( self.__toSplitDict( other ) )
    
    #//-------------------------------------------------------//
    
    def   __str__( self ):
      return separator.join( sorted( "%s=%s" % (key,value) for key, value in self.items() ) )
  
  #//=======================================================//
  
  return SplitDict

#//===========================================================================//

def   ValueDictType( dict_type, key_type, default_value_type = None ):
  
  class   _ValueDict (dict_type):
    
    __VALUE_TYPES = {}
    
    #//-------------------------------------------------------//
    
    @staticmethod
    def   _toValue( key, value, val_types = __VALUE_TYPES, val_type = default_value_type ):
      try:
        if val_type is None:
          val_type = val_types[ key ]
        if isinstance(value, val_type):
          return value
        value = val_type( value )
      except KeyError:
        pass
      
      _ValueDict.setValueType( key, type(value) )
      return value
    
    #//-------------------------------------------------------//
    
    @staticmethod
    def   setValueType( key, value_type, value_types = __VALUE_TYPES, default_type = default_value_type ):
      if default_type is None:
        
        if value_type is list:
          value_type = List
        
        if value_type is dict:
          value_type = Dict
        
        value_types[ key ] = value_type
    
    #//-------------------------------------------------------//
    
    @staticmethod
    def   __toItems( items ):
      if isinstance( items, _ValueDict ):
        return items
      
      items_tmp = []
      
      try:
        for key, value in Dict.toItems( items ):
          key = key_type( key )
          value = _ValueDict._toValue( key, value )
          items_tmp.append( (key, value) )
        
        return items_tmp
      except ValueError:
        raise
    
    #//-------------------------------------------------------//
    
    @staticmethod
    def   __toValueDict( items ):
      if isinstance( items, _ValueDict ):
        return items
      elif isinstance( items, DictItem ):
        key, value = items
        key = key_type( key )
        value = _ValueDict._toValue( key, value )
        return DictItem( key, value )
      
      return _ValueDict( items )
    
    #//-------------------------------------------------------//
    
    def   __init__( self, values = None ):
      super(_ValueDict,self).__init__( self.__toItems( values ) )
    
    def   __iadd__( self, values ):
      return super(_ValueDict,self).__iadd__( self.__toItems( values ) )
    
    def   get( self, key, default = None ):
      return super(_ValueDict,self).get( key_type( key ), default )
    
    def   __getitem__( self, key ):
      return super(_ValueDict,self).__getitem__( key_type( key ) )
    
    def   __setitem__( self, key, value ):
      key = key_type( key )
      return super(_ValueDict,self).__setitem__( key, _ValueDict._toValue( key, value ) )
    
    def   __delitem__( self, key ):
      return super(_ValueDict,self).__delitem__( key_type(key) )
    
    def   pop( self, key, *args ):
      return super(_ValueDict,self).pop( key_type(key), *args )
    
    #//-------------------------------------------------------//
    
    def setdefault(self, key, default ):
      key = key_type(key)
      default = _ValueDict._toValue( key, default )
      
      return super(_ValueDict,self).setdefault( key, default )
    
    #//-------------------------------------------------------//
    
    def update(self, other = None, **kwargs):
      
      other = self.__toItems( other )
      
      super(_ValueDict,self).update( other )
      
      items = self.__toItems( kwargs )
      
      super(_ValueDict,self).update( items )
    
    #//-------------------------------------------------------//
    
    def   __eq__( self, other ):
      return super(_ValueDict,self).__eq__( self.__toValueDict( other ) )
    def   __ne__( self, other ):
      return super(_ValueDict,self).__ne__( self.__toValueDict( other ) )
    def   __lt__( self, other ):
      return super(_ValueDict,self).__lt__( self.__toValueDict( other ) )
    def   __le__( self, other ):
      return super(_ValueDict,self).__le__( self.__toValueDict( other ) )
    def   __gt__( self, other ):
      return super(_ValueDict,self).__gt__( self.__toValueDict( other ) )
    def   __ge__( self, other ):
      return super(_ValueDict,self).__ge__( self.__toValueDict( other ) )
    
    #//-------------------------------------------------------//
  
    def   __contains__( self, key ):
      return super(_ValueDict,self).__contains__( key_type(key) )
  
  #//=======================================================//
  
  return _ValueDict
