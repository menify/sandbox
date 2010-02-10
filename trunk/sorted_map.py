from bisect import bisect_left, insort

class BisectionMap(object):
    
    class Node (object):
        __slots__ = ('key', 'value')
        def     __init__(self, key, value ):
            self.key = key
            self.value = value
        
        def   __lt__( self, other ):
          return self.key < other.key
    
    #//-------------------------------------------------------//
    
    __slots__ = ( 'nodes')
    
    #//-------------------------------------------------------//
    
    def __init__(self, dict = {} ):
        self.nodes = []
        
        for key, value in dict.iteritems():
            self[ key ] = value
    
    #//-------------------------------------------------------//
    
    def __str__(self):
        return '{'+ ', '.join( map(lambda node: repr(node.key) + ': ' + repr(node.value), self.nodes) ) + '}'
    
    #//-------------------------------------------------------//
    
    def __repr__(self):
        return "<BisectionMap object " + str(self) + ">"
    
    #//-------------------------------------------------------//
    
    def __getitem__(self, key, bisect_left = bisect_left ):
        nodes = self.nodes
        key = BisectionMap.Node( key, None )
        pos = bisect_left( nodes, key )
        try:
            node = nodes[pos]
            if not (key < node):
                return node.value
                
        except IndexError:
            pass
        
        raise KeyError(str(key))
    
    #//-------------------------------------------------------//
    
    def __setitem__(self, key, value, bisect_left = bisect_left ):
        nodes = self.nodes
        
        node = BisectionMap.Node( key, value )
        
        pos = bisect_left( nodes, node )
        try:
            if not (node < nodes[pos]):
                nodes[pos] = node
                return
        
        except IndexError:
            pass
        
        nodes.insert( pos, node )
    
    #//-------------------------------------------------------//
    
    def __delitem__(self, key):
        nodes = self.nodes
        key = BisectionMap.Node( key, None )
        pos = bisect_left( nodes, key )
        try:
            if not( key < nodes[pos]):
              del nodes[pos]
        
        except IndexError:
            pass
        
        raise KeyError(str(key))
    
    #//-------------------------------------------------------//
    
    def __contains__(self, key):
        nodes = self.nodes
        key = BisectionMap.Node( key, None )
        pos = bisect_left( nodes, key )
        try:
            if not( key < nodes[pos]):
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
        nodes = self.nodes
        node = BisectionMap.Node( key, value )
        pos = bisect_left( nodes, node )
        try:
            if not (node < nodes[pos]):
                return nodes[pos].value
            
        except IndexError:
            pass
        
        nodes.insert( pos, node )
        return value
    
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
            yield node.value
    
    #//-------------------------------------------------------//
    
    def iterkeys(self):
        for node in self.nodes:
            yield node.key
    
    #//-------------------------------------------------------//
    
    def iteritems(self):
        for node in self.nodes:
            yield ( node.key, node.value )
    
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
