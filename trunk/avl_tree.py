from collections import deque

class AvlMap (object):
    
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
            if direction is -1:
                return self.left
            
            return self.right
        
        #//-------------------------------------------------------//
        
        def __setitem__(self, direction, node ):
            if direction is -1:
                self.left = node
            else:
                self.right = node
            
            if node is not None:
                node.top = self
        
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
        
        node[direction] = right
        node.balance = 0
        
        top[ -direction ] = node
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
        
        left[ neg_direction ] = top_left
        node[ direction ]=  top_right
        
        if top.balance is neg_direction:
            left.balance = direction
            node.balance = 0
        elif top.balance is direction:
            node.balance = neg_direction
            left.balance = 0
        else:
            node.balance = 0
            left.balance = 0
        
        top[ direction ] = left
        top[ neg_direction ] = node
        top.balance = 0
        
        if node_top is None:
            self.head = top
            top.top = None
        else:
            node_top.replace( node, top )
    
    #//-------------------------------------------------------//
    
    def     find( self, value ):
        head = self.head
        
        while head is not None:
            if value < head.value:
                head = head.left
            elif head.value < value:
                head = head.right
            else:
                return head
        
        return None
    
    #//-------------------------------------------------------//
    
    def     depth( self, value ):
        
        node = self.find( value )
        depth = -1
        
        while node is not None:
            depth += 1
            node = node.top
        
        return depth
    
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
        tree.insert( n )
        depth = int(math.log(count, 2)) + 1
        if tree.depth( n ) > depth:
            tree.dump()
            assert not "tree.depth( n ) > depth"
        count += 1
    
    tree_depth = int(math.log(count - 1, 2)) + 1
    for n in random_numbers:
        assert tree.depth( n ) <= tree_depth
    
    #//-------------------------------------------------------//
    import gpl_avl_tree
    
    def   cmpAvlTrees( node, gpl_node ):
        if (node is None) and (gpl_node is None):
            return True
        
        if (node is None) or (gpl_node is None):
            return False
        
        gpl_left, gpl_value, gpl_right, gpl_balance = gpl_node
        
        if node.value != gpl_value:
            return False
        
        return cmpAvlTrees( node.left, gpl_left ) and \
               cmpAvlTrees( node.right, gpl_right )
    
    gpl_tree = gpl_avl_tree.AVLTree()
    tree = AvlTree()
    
    random.seed(0)
    random_numbers = range(50000, 49000, -1)
    random.shuffle( random_numbers )
    
    class Foo (object):
        __slots__ = ( 'key', 'value' )
        def     __init__(self, n ):
            self.key = n
            self.value = n
        
        def __cmp__(self, other, isinstance = isinstance, cmp = cmp, int = int ):
            if isinstance(other, int):
                return cmp(self.key, other)
            
            return cmp(self.key, other.key)
        
        def __lt__(self, other ):
            return self.key < other.key
    
    foo_random_numbers = map(Foo, random_numbers)
    
    import time
    now_time = time.clock()
    for i in xrange(0,1000):
        tree = AvlTree()
        for n in random_numbers:
            tree.insert( n )
    print "AvlTree time:", time.clock() - now_time
    
    #~ now_time = time.clock()
    #~ for n in random_numbers:
        #~ gpl_tree.insert( Foo(n) )
    #~ print "GPL AVLTree time:", time.clock() - now_time
    
    now_time = time.clock()
    for i in xrange(0,1000):
        rb_tree = RBTree.RBTree()
        for n in random_numbers:
            rb_tree.insertNode( n, n )
    print "RBTree time:", time.clock() - now_time
    
    #~ tree.insert( 10001 )
    import bisect
    now_time = time.clock()
    for i in xrange(0,1000):
        bi_list = []
        for n in foo_random_numbers:
            bisect.insort( bi_list, n )
    print "bisect time:", time.clock() - now_time
    
    now_time = time.clock()
    for i in xrange(0,1000):
        for n in foo_random_numbers:
          bisect.bisect_left( bi_list, n )
    print "bisect find time:", time.clock() - now_time
    
    now_time = time.clock()
    for i in xrange(0,1000):
        for n in random_numbers:
            tree.find( n )
    print "AvlTree find time:", time.clock() - now_time
    
    now_time = time.clock()
    for i in xrange(0,1000):
        for n in random_numbers:
            rb_tree.findNode( n )
    print "RBTree find time:", time.clock() - now_time
    
    #~ print cmpAvlTrees( tree.head, gpl_tree.tree )
    
    print "Tests passed"
