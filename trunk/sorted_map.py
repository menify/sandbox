from bisect import bisect_left, insort

class BisectionMap(object):
    
    __slots__ = ( 'key_values', 'key_type' )
    
    def   KeyValue( self, key, value ):
      if self.key_type is None:
        class _KeyValue (type(key)):
            __slots__ = ('key_value')
            def     __new__(cls, key, value ):
                self = super(_KeyValue, cls).__new__( cls, key )
                self.key_value = value
                return self
            
        self.key_type = _KeyValue
      
      return self.key_type( key, value )
    
    #//-------------------------------------------------------//
    
    def __init__(self, dict = {} ):
        self.key_type = None
        self.key_values = []
        
        for key, value in dict.iteritems():
            self[ key ] = value
    
    #//-------------------------------------------------------//
    
    def __str__(self):
        return '{'+ ', '.join( map(lambda key_value: repr(key_value) + ': ' + repr(key_value.key_value), self.key_values) ) + '}'
    
    #//-------------------------------------------------------//
    
    def __repr__(self):
        return "<BisectionMap object " + str(self) + ">"
    
    #//-------------------------------------------------------//
    
    def __getitem__(self, key, bisect_left = bisect_left ):
        key_values = self.key_values
        pos = bisect_left( key_values, key )
        try:
            value_key = key_values[pos]
            if not (key < value_key):
                return value_key.key_value
                
        except IndexError:
            pass
        
        raise KeyError(str(key))
    
    #//-------------------------------------------------------//
    
    def __setitem__(self, key, value, bisect_left = bisect_left ):
        key_values = self.key_values
        
        key_value = self.KeyValue( key, value )
        
        pos = bisect_left( key_values, key_value )
        try:
            if not (key_value < key_values[pos]):
                key_values[pos] = key_value
                return
        
        except IndexError:
            pass
        
        key_values.insert( pos, key_value )
    
    #//-------------------------------------------------------//
    
    def __delitem__(self, key):
        key_values = self.key_values
        pos = bisect_left( key_values, key )
        try:
            if not( key < key_values[pos]):
              del key_values[pos]
        
        except IndexError:
            pass
        
        raise KeyError(str(key))
    
    #//-------------------------------------------------------//
    
    def __contains__(self, key):
        key_values = self.key_values
        pos = bisect_left( key_values, key )
        try:
            if not( key < key_values[pos]):
              return True
        
        except IndexError:
            pass
        
        return False
    
    #//-------------------------------------------------------//
    
    def has_key(self, key):
        return self.__contains__(key);
    
    #//-------------------------------------------------------//
    
    def get(self, key, default = None):
        try:
            return self[key]
        except KeyError:
            return default
    
    #//-------------------------------------------------------//
    
    def setdefault(self, key, value = None ):
        key_values = self.key_values
        pos = bisect_left( key_values, key )
        try:
            value_key = key_values[pos]
            if not(key < value_key):
                return value_key.key_value
            
        except IndexError:
            pass
        
        key_value = self.KeyValue( key, value )
        key_values.insert( pos, key_value )
        return key_value
    
    #//-------------------------------------------------------//
    
    def keys(self):
        return tuple( self.iterkeys() )
    
    #//-------------------------------------------------------//
    
    def values(self):
        return tuple( self.itervalues() )
    
    #//-------------------------------------------------------//
    
    def items(self):
        return tuple( self.iteritems() )
    
    #//-------------------------------------------------------//
    
    def itervalues(self):
        for kv in self.key_values:
            yield kv.key_value
    
    #//-------------------------------------------------------//
    
    def iterkeys(self):
        for kv in self.key_values:
            yield kv
    
    #//-------------------------------------------------------//
    
    def iteritems(self):
        for kv in self.key_values:
            yield ( kv, kv.key_value )
    
    #//-------------------------------------------------------//
    
    def __iter__(self):
        return self.iterkeys()
    
    #//-------------------------------------------------------//

    def clear(self):
        self.key_values = []
        self.key_type = None
    
    #//-------------------------------------------------------//
    
    def copy(self):
        clone = BisectionMap()
        clone.key_values = list(self.key_values)
        clone.key_type = self.key_type
        
        return clone
    
    #//-------------------------------------------------------//
    
    def update(self, other):
        for key in other.iterkeys():
            self[key] = other[key]

if __name__ == "__main__":
    
    import random
    import time
    loop_count = 1000
    
    random.seed()
    random_numbers = range(0,10)
    random.shuffle( random_numbers )
    random_numbers += random_numbers
    
    now_time = time.clock()
    for i in xrange(0, loop_count):
        bi_map = BisectionMap()
        for n in random_numbers:
            bi_map[n] = -2 * n
        
        for n in random_numbers:
            v = bi_map[n]
    print "BisectionMap time:", time.clock() - now_time
    
    print bi_map.values()
    print bi_map.keys()
    print bi_map.items()
    print repr(bi_map)
    print repr(dict(bi_map))
    
    now_time = time.clock()
    for i in xrange(0, loop_count):
        hash_map = dict()
        for n in random_numbers:
            hash_map[n] = -2 * n
        
        for n in random_numbers:
            v = hash_map[n]
    print "dict time:", time.clock() - now_time
