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
                self.__rotate( top, direction, node_direction )
                break
            
            node = top
            node_direction = direction
    
    #//-------------------------------------------------------//
    
    def   __rotate(self, node, direction, next_direction ):
        if direction is next_direction:
            self.__rotateDirect( node, direction )
        else:
            if direction is -1:
                self.__rotateLeftRight( node )
            else:
                self.__rotateRightLeft( node )
    
    #//-------------------------------------------------------//
    
    def   __rotateDirect( self, node, direction ):
        top = node[direction]
        left = top[-direction]
        node_top = node.top
        
        top.top = node_top
        top[-direction] = node
        top.balance = 0
        
        node.balance = 0
        node[direction] = left
        node.top = top
        
        if left is not None:
          left.top = node
        
        if node_top is None:
            self.head = top
        else:
            if node_top.left is node:
                node_top.left = top
            else:
                node_top.right = top
    
    #//-------------------------------------------------------//
    
    def   __rotateIndirect( self, node, direction, next_direction ):
        left = node[direction]
        node_top = node.top
        
        top = left[-direction]
        top_left = top[direction]
        top_right = top[-direction]
        
        dir_node.top = node_top
        dir_node[-direction] = node
        dir_node.balance = 0
        
        node.balance = 0
        node[direction] = dir_moved_node
        node.top = dir_node
        
        if dir_moved_node is not None:
          dir_moved_node.top = node
        
        if node_top is None:
            self.head = dir_node
        else:
            if node_top.left is node:
                node_top.left = dir_node
            else:
                node_top.right = dir_node
    
    #//-------------------------------------------------------//
    
    def   __rotateLeftRight( self, node ):
        assert not "Not implemented"
        #~ left_node = node.left
        #~ left_right_node = left_node.right
        
        #~ left_right_node.top = node.top
        #~ left_right_node.right = node
        #~ left_right_node.left = left_node
        #~ left_right_node.balance = 0
        
        
        #~ left_node.right = left_right_node.left
        #~ node.left = left_right_node.right
        
        #~ left_node.top
        
        
        #~ node.balance = 0
        #~ node.left = left_right_node
        #~ left_right_node.top = node
        
        #~ left_node.right = node
        #~ left_node.balance = 0
    
    #//-------------------------------------------------------//
    
    def   __rotateRightLeft( self, node ):
        assert not "Not implemented"
    
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
    
    tree_depth = int(math.log(count - 1, 2))
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
    
    print "Tests passed"
