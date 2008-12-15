#include <iostream>

#include "sbe/list/intrusive_list.hpp"


struct FooList: public sbe::IntrusiveList<FooList>
{
};


//---------------------------------------------------------------------------//

static void     test_foolist( void )
{
    FooList     nodes[10];
    FooList*    root = &nodes[0];
    
    for (size_t  i = 1; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        root->pushBack( &nodes[i] );
        
        SBE_ASSERT(nodes[i-1].next() == &nodes[i]);
        SBE_ASSERT(nodes[i].previous() == &nodes[i-1]);
        SBE_ASSERT(const_cast<FooList const *>(&nodes[i-1])->next() == &nodes[i]);
        SBE_ASSERT(const_cast<FooList const *>(&nodes[i])->previous() == &nodes[i-1]);
    }
    
    SBE_ASSERT( root->test() );
    
    //-------------------------------------------------------//
    
    FooList     nodes2[5];
    FooList*    root2 = &nodes2[0];
    
    for (size_t  i = 1; i < sizeof(nodes2)/sizeof(nodes2[0]); ++i)
    {
        root2->pushFront( &nodes2[i] );
    }
    
    SBE_ASSERT( root2->test() );
    
    root->pushBack( root2 );
    
    SBE_ASSERT( root->test() );
    
    //-------------------------------------------------------//
    
    FooList     nodes3[5];
    FooList*    root3 = &nodes3[0];
    
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
        SBE_ASSERT( nodes2[i].test() );
    }
    
    SBE_ASSERT( root->test() );
    
    std::cout << "Test: 'test_foolist' - " << "PASSED" << std::endl;
}

int main( void )
{
    test_foolist();
    
    return 0;
}
 
