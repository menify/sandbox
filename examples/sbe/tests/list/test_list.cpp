#include <iostream>

#include "sbe/list/list.hpp"


struct FooItem: public sbe::ListItem<FooItem>
{
    size_t      index;
    
    inline FooItem( void )  : index (0) {}
    inline ~FooItem( void )             {}
    
    explicit inline FooItem( size_t  in_index )  : index (in_index) {}
    FooItem( FooItem const & item )     : sbe::ListItem<FooItem>(), index (item.index)    {}
    FooItem& operator=( FooItem const & item )
    {
        this->index = item.index;
        return *this;
    }
};

bool    operator==( FooItem const &  item1, FooItem const &  item2 )
{
    return item1.index == item2.index;
}

typedef sbe::List<FooItem>  FooList;

//---------------------------------------------------------------------------//

static void     test_listitem( void )
{
    FooItem     nodes[10];
    FooItem*    root = &nodes[0];
    
    for (size_t  i = 0; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        nodes[i].index = i;
    }
    
    SBE_ASSERT(root->find( FooItem( nodes[0] )) == &nodes[0]);
    SBE_ASSERT(root->find( FooItem( 1 )) == NULL);
    SBE_ASSERT(root->find( FooItem( 2 )) == NULL);
    
    for (size_t  i = 1; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        root->pushBack( &nodes[i] );
        SBE_ASSERT(root->find( FooItem( i )) == &nodes[i]);
        
        SBE_ASSERT(nodes[i-1].next() == &nodes[i]);
        SBE_ASSERT(nodes[i].previous() == &nodes[i-1]);
        SBE_ASSERT(const_cast<FooItem const *>(&nodes[i-1])->next() == &nodes[i]);
        SBE_ASSERT(const_cast<FooItem const *>(&nodes[i])->previous() == &nodes[i-1]);
    }
    
    SBE_ASSERT( root->test() );
    
    //-------------------------------------------------------//
    
    FooItem     nodes2[5];
    FooItem*    root2 = &nodes2[0];
    
    SBE_ASSERT(root->find( FooItem( 0 )) == root);
    
    for (size_t  i = 1; i < sizeof(nodes2)/sizeof(nodes2[0]); ++i)
    {
        root2->pushFront( &nodes2[i] );
    }
    
    SBE_ASSERT( root2->test() );
    
    root->pushBack( root2 );
    
    SBE_ASSERT( root->test() );
    
    //-------------------------------------------------------//
    
    FooItem     nodes3[5];
    FooItem*    root3 = &nodes3[0];
    
    for (size_t  i = 1; i < sizeof(nodes3)/sizeof(nodes3[0]); ++i)
    {
        root3->pushBack( &nodes3[i] );
    }
    
    SBE_ASSERT( root3->test() );
    
    root->pushFront( root3 );
    
    SBE_ASSERT( root->test() );
    
    //-------------------------------------------------------//
    
    for (size_t  i = 1; i < sizeof(nodes2)/sizeof(nodes2[0]); ++i)
    {
        nodes2[i].pop();
        SBE_ASSERT( nodes2[i].single() );
        nodes2[i].pop();
        SBE_ASSERT( nodes2[i].single() );
        SBE_ASSERT( nodes2[i].test() );
    }
    
    SBE_ASSERT( root->test() );
    
    std::cout << "Test: 'test_listitem' - " << "PASSED" << std::endl;
}

static void test_list( void )
{
    FooItem     nodes[10];
    FooList     head;
    
    for (size_t  i = 0; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        nodes[i].index = i;
    }
    
    SBE_ASSERT( head.find( FooItem(0) ) == NULL );
    
    for (size_t  i = 0; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        head.pushBack( &nodes[i] );
        SBE_ASSERT( head.find( FooItem(i) ) == &nodes[i] );
        
        SBE_ASSERT( head.back() == &nodes[i] );
        SBE_ASSERT( head.front() == nodes[i].next() );
        SBE_ASSERT( head.front() == &nodes[0] );
    }
    
    for (size_t  i = 0; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        FooItem*    next = head.front()->next();
        if (next == head.front())
        {
            next = NULL;
        }
        
        FooItem*    item = head.front();
        SBE_ASSERT( item == head.popFront() );
        SBE_ASSERT( head.front() == next );
    }
    
    SBE_ASSERT( head.front() == NULL );
    
    for (size_t  i = 0; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        FooItem*    item = head.front();
        
        head.pushFront( &nodes[i] );
        
        SBE_ASSERT( (item == NULL) || (head.front()->next() == item) );
        SBE_ASSERT( (item == NULL) || (item->previous() == head.front()) );
        SBE_ASSERT( head.front() == &nodes[i] );
    }
    
    for (size_t  i = 0; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        FooItem*    back = head.back();
        SBE_ASSERT( back == head.popBack() );
    }
    
    SBE_ASSERT( head.front() == NULL );
    SBE_ASSERT( head.back() == NULL );
    
    SBE_ASSERT( head.popFront() == NULL );
    SBE_ASSERT( head.popBack() == NULL );
    
    std::cout << "Test: 'test_list' - " << "PASSED" << std::endl;
}

int main( void )
{
    test_listitem();
    test_list();
    
    return 0;
}
 
