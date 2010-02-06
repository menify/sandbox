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
            if node_top.left is node:
                node_top.left = left_node
            else:
                node_top.right = left_node
    
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
    tree = AvlTree()
    
    tree.insert(10); tree.dump()
    tree.insert(9); tree.dump()
    tree.insert(8); tree.dump()
    tree.insert(7); tree.dump()
    tree.insert(6); tree.dump()
    tree.insert(5); tree.dump()
