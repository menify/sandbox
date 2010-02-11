from bisect import bisect_left

class BisectionMap(object):
    
    __slots__ = ('nodes')
    
    #//-------------------------------------------------------//
    
    def __init__(self, dict = {} ):
        self.nodes = []
        
        for key, value in dict.iteritems():
            self[ key ] = value
    
    #//-------------------------------------------------------//
    
    def __findPosition( self, key ):
        
        nodes = self.nodes
        
        pos = 0
        end = len(nodes)
        while pos < end:
            mid = (pos + end) // 2
            if nodes[mid][0] < key:
                pos = mid + 1
            else:
                end = mid
        
        try:
            node = nodes[pos]
            if not (key < node[0]):
                return pos, node
                
        except IndexError:
            pass
        
        return pos, None
    
    #//-------------------------------------------------------//
    
    def __getitem__(self, key ):
        
        pos, node = self.__findPosition( key )
        if node is None:
            raise KeyError(str(key))
        
        return node[1]
    
    #//-------------------------------------------------------//
    
    def __setitem__(self, key, value ):
        pos, node = self.__findPosition( key )
        if node is not None:
            node[1] = value
        else:
          self.nodes.insert( pos, [ key, value ] )
    
    #//-------------------------------------------------------//
    
    def setdefault(self, key, value = None ):
        pos, node = self.__findPosition( key )
        if node is not None:
            return node[1]
        
        self.nodes.insert( pos, [key, value] )
        return value
    
    #//-------------------------------------------------------//
    
    def __delitem__(self, key):
        pos, node = self.__findPosition( key )
        if node is not None:
            del nodes[pos]
        
        raise KeyError(str(key))
    
    #//-------------------------------------------------------//
    
    def __contains__(self, key):
        return self.__findPosition( key )[1] is not None
    
    #//-------------------------------------------------------//
    
    def has_key(self, key):
        return self.__findPosition( key )[1] is not None
    
    #//-------------------------------------------------------//
    
    def get(self, key, default = None):
        try:
            return self[key]
        except KeyError:
            return default
    
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
        for node in self.nodes:
            yield node[1]
    
    #//-------------------------------------------------------//
    
    def iterkeys(self):
        for node in self.nodes:
            yield node[0]
    
    #//-------------------------------------------------------//
    
    def iteritems(self):
        for node in self.nodes:
            yield ( node[0], node[1] )
    
    #//-------------------------------------------------------//
    
    def __iter__(self):
        return self.iterkeys()
    
    #//-------------------------------------------------------//
    
    def clear(self):
        self.nodes = []
    
    #//-------------------------------------------------------//
    
    def copy(self):
        clone = BisectionMap()
        clone.nodes = list(self.nodes)
        
        return clone
    
    #//-------------------------------------------------------//
    
    def update(self, other):
        for key in other.iterkeys():
            self[key] = other[key]
    
    #//-------------------------------------------------------//
    
    def __str__(self):
        return '{'+ ', '.join( map(lambda node: repr(node[0]) + ': ' + repr(node[1]), self.nodes) ) + '}'
    
    #//-------------------------------------------------------//
    
    def __repr__(self):
        return self.__str__()
