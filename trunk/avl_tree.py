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
    
    class Step (object):
        __slots__ = ( 'node', 'direction' )
        def     __init__( self, node, direction ):
            assert isinstance( node, AvlTree.Node )
            assert direction in (-1, 1)
            
            self.node = node
            self.direction = direction
    
    #//-------------------------------------------------------//
    
    def     __init__( self ):
        self.head = None
    
    #//-------------------------------------------------------//
    
    def     __rebalance( self, path ):
        
        prev_step = None
        
        for step in path:
            node = step.node
            balance = step.direction + node.balance
            if balance == 0:
                node.balance = 0
                break   # no rebalance needed
            
            elif balance in (1, -1):
                node.balance = balance
                prev_step = step
            
            else:
                self.__rotate( node, prev_step.direction, step.direction )
                break
    
    #//-------------------------------------------------------//
    
    def   __rotate(self, node, direction, next_direction ):
        if direction == next_direction:
            if direction == -1:
                self.__rotateLeftLeft( node )
            else:
                self.__rotateRightRight( node )
        else:
            if direction == -1:
                self.__rotateLeftRight( node )
            else:
                self.__rotateRightLeft( node )
    
    #//-------------------------------------------------------//
    
    def   __rotateLeftLeft( self, node ):
        left_node = node.left
        left_right_node = left_node.right
        node_top = node.top
        
        left_node.top = node_top
        left_node.right = node
        left_node.balance = 0
        
        node.balance = 0
        node.left = left_right_node
        node.top = left_node
        
        if left_right_node is not None:
          left_right_node.top = node
        
        if node_top is None:
            self.head = left_node
        else:
            
    
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
    
    #~ #//-------------------------------------------------------//
    
    def   __rotateRightRight( self, node ):
        assert not "Not implemented"
        #~ right_node = node.right
        #~ right_left_node = right_node.left
        
        #~ node.balance = 0
        #~ node.right = right_left_node
        #~ right_left_node.top = node
        
        #~ right_node.left = node
        #~ right_node.balance = 0
    
    #//-------------------------------------------------------//
    
    def   __rotateRightLeft( self, node ):
        assert not "Not implemented"
    
    #//-------------------------------------------------------//
    
    def     insert( self, value ):
        
        head = self.head
        
        if head is None:
            self.head = AvlTree.Node( value )
            return
        
        path = deque()
        
        while True:
            head_value = head.value
            
            if value < head_value:
                path.appendleft( AvlTree.Step( head, -1 ) )
                head_left = head.left
                if head_left is None:
                    head.left = AvlTree.Node( value, head )
                    self.__rebalance( path )
                    return
                else:
                    head = head_left
            
            elif head_value < value:
                path.appendleft( Step( head, 1 ) )
                head_right = head.right
                if head_right is None:
                    head.right = AvlTree.Node( value, head )
                    self.__rebalance( path )
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
        #~ else:
            #~ print " " * indent + str(None)
        
        if node.right is not None:
            self.dump( node.right, indent )
        #~ else:
            #~ print " " * indent + str(None)

if __name__ == "__main__":
    tree = AvlTree()
    
    tree.insert(10)
    tree.insert(9)
    tree.insert(8)
    tree.insert(7)
    tree.insert(6)
    tree.dump()
