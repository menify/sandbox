from collections import deque

class AvlTree (object):
    
    class Node (object):
        __slots__ = ( 'top', 'left', 'right', 'value', 'balance' )
        
        def __init__( self, value, top = None ):
            assert (top is None) or (type( top ) is type(self))
            
            self.top = top
            self.left = None
            self.right = None
            self.value = value
            self.balance = 0
        
        #//-------------------------------------------------------//
        
        def attach( self, direction, node ):
            self[direction] = node
            if node is not None:
                node.top = self
        
        #//-------------------------------------------------------//
        
        def detach( self, node ):
            assert (node is self.left) or (node is self.right)
            
            if self.left is node:
                self.left = None
            else:
                self.right = None
            
            if node is not None:
                node.top = None
        
        #//-------------------------------------------------------//
        
        def replace( self, old_node, new_node ):
            if self.left is old_node:
                self.left = new_node
            else:
                self.right = new_node
            
            if new_node is not None:
                new_node.top = self
        
        #//-------------------------------------------------------//
        
        def __getitem__(self, direction ):
            if __debug__:
                if (direction is not 1) and (direction is not -1):
                    raise IndexError('Invalid direction: %s' % direction )
            
            if direction is -1:
                return self.left
            
            return self.right
        
        #//-------------------------------------------------------//
        
        def __setitem__(self, direction, node ):
            if __debug__:
                if (direction is not 1) and (direction is not -1):
                    raise IndexError( 'Invalid direction: %s' % direction )
                
                assert (node is None) or (type( node ) is type(self))
            
            if direction is -1:
                self.left = node
            else:
                self.right = node
        
        #//-------------------------------------------------------//
        
        def   __str__(self):
            return str(self.value)
    
    #//=======================================================//
    
    def     __init__( self ):
        self.head = None
    
    #//-------------------------------------------------------//
    
    def     __rebalance( self, node ):
        assert node is not None
        
        while True:
            top = node.top
            if top is None:
                break
            
            if top.left is node:
                direction = -1
            else:
                direction = 1
            
            balance = direction + top.balance
            top.balance = balance
            if balance is 0:
                break   # rebalance is not needed anymore
            
            elif (balance is not -1) and (balance is not 1):
                self.__rotate( top, direction )
                break
            
            node = top
    
    #//-------------------------------------------------------//
    
    def   __rotate(self, node, direction ):
        if direction is node[direction].balance:
            self.__rotateDirect( node, direction )
        else:
            self.__rotateIndirect( node, direction )
    
    #//-------------------------------------------------------//
    
    def   __rotateDirect( self, node, direction ):
        top = node[direction]
        right = top[-direction]
        node_top = node.top
        
        node.attach( direction, right )
        node.balance = 0
        
        top.attach( -direction, node )
        top.balance = 0
        
        if node_top is None:
            self.head = top
            top.top = None
        else:
            node_top.replace( node, top )
    
    #//-------------------------------------------------------//
    
    def   __rotateIndirect( self, node, direction ):
        neg_direction = -direction
        
        node_top = node.top
        left = node[direction]
        top = left[neg_direction]
        top_left = top[direction]
        top_right = top[neg_direction]
        
        left.attach( neg_direction, top_left )
        node.attach( direction, top_right )
        
        if top.balance is neg_direction:
            left.balance = direction
            node.balance = 0
        elif top.balance is direction:
            node.balance = neg_direction
            left.balance = 0
        else:
            node.balance = 0
            left.balance = 0
        
        top.attach( direction, left )
        top.attach( neg_direction, node )
        top.balance = 0
        
        if node_top is None:
            self.head = top
            top.top = None
        else:
            node_top.replace( node, top )
    
    #//-------------------------------------------------------//
    
    def     depth( self, value ):
        
        head = self.head
        depth = 0
        
        if head is None:
            return -1
        
        while True:
            if value < head.value:
                if head.left is not None:
                    head = head.left
                else:
                    return -1
            
            elif head.value < value:
                if head.right is not None:
                    head = head.right
                else:
                    return -1
            else:
                return depth
            
            depth += 1
    
    #//-------------------------------------------------------//
    
    def     insert( self, value ):
        
        head = self.head
        
        if head is None:
            self.head = AvlTree.Node( value )
            return
        
        while True:
            head_value = head.value
            
            if value < head_value:
                head_left = head.left
                if head_left is None:
                    node = AvlTree.Node( value, head )
                    head.left = node
                    self.__rebalance( node )
                    return
                else:
                    head = head_left
            
            elif head_value < value:
                head_right = head.right
                if head_right is None:
                    node = AvlTree.Node( value, head )
                    head.right = node
                    self.__rebalance( node )
                    return
                else:
                    head = head_right
            else:
                return
    
    #//-------------------------------------------------------//
    
    def dump( self, node = None, indent = 0 ):
        
        if node is None:
            node = self.head
        
        print " " * indent + str(node.value) + '(' + str(node.balance) + ')'
        indent += 2
        if node.left is not None:
            self.dump( node.left, indent )
        else:
            print " " * indent + str(None)
        
        if node.right is not None:
            self.dump( node.right, indent )
        else:
            print " " * indent + str(None)

if __name__ == "__main__":
    
    import math
    import RBTree
    
    #//=======================================================//
    
    tree = AvlTree();
    
    count = 1
    for i in xrange(10, -1, -1):
        tree.insert(i);
        depth = int(math.log(count, 2))
        assert tree.depth( i ) == depth
        count += 1
    
    tree_depth = int(math.log(count - 1, 2)) + 1
    for i in xrange(10, -1, -1):
        assert tree.depth( i ) <= tree_depth
    
    tree = AvlTree();
    count = 1
    
    for i in xrange(0, 10, 1):
        tree.insert(i);
        depth = int(math.log(count, 2))
        assert tree.depth( i ) == depth
        count += 1
    
    tree_depth = int(math.log(count - 1, 2))
    for i in xrange(0, 10, 1):
        assert tree.depth( i ) <= tree_depth
    
    #//-------------------------------------------------------//
    import random
    
    random.seed(0)
    random_numbers = range(0,100)
    random.shuffle( random_numbers )
    
    tree = AvlTree();
    count = 1
    for n in random_numbers:
        print "inserting:", n
        tree.insert( n )
        depth = int(math.log(count, 2)) + 1
        print "tree.depth( n ):", tree.depth( n )
        print "depth:", depth
        if tree.depth( n ) > depth:
            tree.dump()
            assert not "tree.depth( n ) > depth"
        count += 1
    
    tree_depth = int(math.log(count - 1, 2)) + 1
    for n in random_numbers:
        assert tree.depth( n ) <= tree_depth
    
    print "Tests passed"
