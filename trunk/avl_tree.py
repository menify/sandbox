from collections import deque

class AvlTree (object):
    
    class Node (object):
        __slots__ = ( 'top', 'left', 'right', 'value', 'balance' )
        
        def __init__( self, value, top = None ):
            assert (top is None) or isintance( top, Node )
            
            self.top = top
            self.left = None
            self.right = None
            self.value = value
            self.balance = 0
    
    class Step (object):
        __slots__ = ( 'node', 'direction' )
        def     __init__( self, node, direction ):
            assert isintance( node, Node )
            assert isintance( direction, int )
            
            self.node = node
            self.direction = direction
    
    #//-------------------------------------------------------//
    
    def     __init__( self ):
        self.head = None
    
    #//-------------------------------------------------------//
    
    def     __rebalance( self, path ):
        
        prev_step = None
        
        for step in path:
            balance = step.direction + node.balance
            if balance == 0:
                node.balance = 0
                break   # no rebalance needed
            
            elif balance in (1, -1):
                node.balance = balance
                prev_step = step
            
            else:
                self.__rotate( node, prev_step.direction, step.direction )
    
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
        
        left_node.top = node.top
        left_node.right = node
        left_node.balance = 0
        
        node.balance = 0
        node.left = left_right_node
        node.top = left_node
        
        left_right_node.top = node
    
    #//-------------------------------------------------------//
    
    def   __rotateLeftRight( self, node ):
        left_node = node.left
        left_right_node = left_node.right
        
        left_right_node.top = node.top
        left_right_node.right = node
        left_right_node.left = left_node
        left_right_node.balance = 0
        
        
        left_node.right = left_right_node.left
        node.left = left_right_node.right
        
        left_node.top
        
        
        node.balance = 0
        node.left = left_right_node
        left_right_node.top = node
        
        left_node.right = node
        left_node.balance = 0
    
    #//-------------------------------------------------------//
    
    def   __rotateRightRight( self, node ):
        right_node = node.right
        right_left_node = right_node.left
        
        node.balance = 0
        node.right = right_left_node
        right_left_node.top = node
        
        right_node.left = node
        right_node.balance = 0
    
    #//-------------------------------------------------------//
    
    def     insert( self, value ):
        
        head = self.head
        
        if head is None:
            self.head = Node( value )
            return
        
        path = deque()
        
        while True:
            head_value = head.value
            
            if value < head_value:
                path.appendleft( Step( head, -1 ) )
                head_left = head.left
                if head_left is None:
                    head.left = Node( value, head )
                    self.__rebalance( path )
                    return
                else:
                    head = head_left
            
            elif head_value < value:
                path.appendleft( Step( head, 1 ) )
                head_right = head.right
                if head_right is None:
                    head.right = Node( value, head )
                    self.__rebalance( path )
                    return
                else:
                    head = head_right
            else:
                return

