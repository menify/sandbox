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
        
        child_balance = 0
        prev_step = None
        
        for step in path:
            child_balance = step.direction + node.balance + child_balance
            if child_balance == 0:
                node.balance = 0
                break   # no rebalance needed
            
            if child_balance == -1 or child_balance == 1:
                node.balance = child_balance
                prev_step = step
            
            else:
                if prev_step.direction == step.direction:
                    
    
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

