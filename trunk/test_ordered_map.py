import random
import time

import sorted_map
import RBTree
import avl_map

class FooKey (object):
    __slots__ = ('value', 'other')
    
    #//-------------------------------------------------------//
    
    def     __init__(self, value, other ):
        self.value = str(value).upper()
        self.other = int(other)
    
    #//-------------------------------------------------------//
    
    def     __str__(self):
        return str(self.value)
    
    #//-------------------------------------------------------//
    
    def     __cmp__(self, other):
        return cmp( self.value.lower(), str(other).lower() )
    
    def     __hash__(self ):
        return hash( self.value.lower() )
    
    #//-------------------------------------------------------//
    
    def __lt__( self, other):       return self.__cmp__(other) < 0
    def __le__( self, other):       return self.__cmp__(other) <= 0
    def __eq__( self, other):       return self.__cmp__(other) == 0
    def __ne__( self, other):       return self.__cmp__(other) != 0
    def __gt__( self, other):       return self.__cmp__(other) > 0
    def __ge__( self, other):       return self.__cmp__(other) >= 0

def     testDict( dict_type ):
    loop_count = 100
    
    random_keys = []
    for key in map( hex, map( id, range(1,500) ) ):
        random_keys.append( FooKey( key.upper(), id(key) ) )
    
    random_keys += random_keys
    
    now_time = time.clock()
    for i in xrange(0, loop_count):
        dict_map = dict_type()
        for n in random_keys:
            dict_map[n] = hex(id(n))
    print str(type(dict_map)) + " append time:", time.clock() - now_time
    
    now_time = time.clock()
    for i in xrange(0, loop_count):
        for n in random_keys:
            v = dict_map.get(n)
    print str(type(dict_map)) + " get time:", time.clock() - now_time

if __name__ == "__main__":
    #~ testDict( dict )
    testDict( sorted_map.BisectionMap )
    #~ testDict( RBTree.RBDict )
    testDict( avl_map.AvlMap )

