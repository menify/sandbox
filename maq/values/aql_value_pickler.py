try:
  import cPickle as pickle
except ImportError:
  import pickle

#//===========================================================================//

class   ValuePickler (object):
  
  __slots__ = ('')
  
  BUILTIN_TYPE  = b'b'
  LIST_TYPE  = b'l'
  TUPLE_TYPE  = b't'
  SET_TYPE  = b's'
  FROZENSET_TYPE  = b'f'
  DICT_TYPE  = b'd'
  UNKNOWN_TYPE  = b'n'
  
  BUILTIN_TYPES = (type(None), bool, int, float, bytes, bytearray, str )
  SEQ_TYPES = (tuple, list, set, frozenset)
  SEQ_PICK_TYPES = (TUPLE_TYPE, LIST_TYPE, SET_TYPE, FROZENSET_TYPE)
  
  pickleable_types = {}
  
  def   __init__( self ):
    pass
  
  #//-------------------------------------------------------//
  
  def   __pickValue( self, buf, value,
                     pickleable_types = pickleable_types,
                     BUILTIN_TYPE = TYPE, DICT_TYPE = DICT_TYPE,
                     LIST_TYPE = LIST_TYPE, TUPLE_TYPE = TUPLE_TYPE,
                     SET_TYPE = SET_TYPE, FROZENSET_TYPE = FROZENSET_TYPE,
                     BUILTIN_TYPES = BUILTIN_TYPES, SEQ_TYPES = SEQ_TYPES )
    
    pickValue = self.__pickValue
    
    value_type = type(value)
    type_name = value_type.__name__
    if type_name in pickleable_types:
      pick_value = {}
      for key,v in value.__getstate__().items():
        pick_value[key] = pickValue( v )
      
      return (type_name, state)
    
    elif value_type in BUILTIN_TYPES:
      return (BUILTIN_TYPE, value)
    
    elif value_type in SEQ_TYPES:
      
      pick_type = LIST_TYPE
      pick_value = []
      
      for v in value:
        pick_value.append( pickValue( v ) )
      
      if value_type is tuple:
        pick_type = TUPLE_TYPE
      
      elif value_type is set:
        pick_type = SET_TYPE
      
      elif value_type is frozenset:
        pick_type = FROZENSET_TYPE
      
      return (pick_type, pick_value)
    
    elif value_type is dict:
      pick_value = {}
      
      for key,v in value.items():
        pick_value[ pickValue( key ) ] = pickValue( v )
      
      return (DICT_TYPE, pick_value)
    
    else:
      return (UNKNOWN_TYPE, pickle.dumps( value, pickle.HIGHEST_PROTOCOL ) )
  
  #//-------------------------------------------------------//
  
  def   __unpickValue( self, pair ):
    pick_type, pick_value = pair
    if pick_type in pickleable_types:
      state = {}
      for key, v in pick_value.items():
        state[key] = unpickValue( v )
      
      value_type = pickleable_types[ pick_type ]
      value = value_type.__new__(value_type)
      value.__setstate__( state )
      
      return value
    elif pick_type == TYPE:
      return pick_value
    
    elif pick_type in SEQ_PICK_TYPES:
      value = []
      for v in pick_value:
        value.append( unpickValue( v) )
      
      if pick_type == TUPLE_TYPE:
        value = 
  
  #//-------------------------------------------------------//
  
  def   dumps( self, value, pickleable = pickleable, pickle_dumps = pickle.dumps):
    
    class_name = value.__class__.__name__
    if class_name in pickleable:
      state = value.__getstate__()
      
    else:
      pickle_dumps( value, pickle.HIGHEST_PROTOCOL )
    

#//===========================================================================//

def  pickleable( value_class ):
  if type(value_class) is type:
    pickleable_types[ value_class.__name__ ] = value_class
  
  return value_class

#//===========================================================================//
