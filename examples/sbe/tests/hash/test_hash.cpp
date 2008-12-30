#include <iostream>

#include "sbe/hash/hash.hpp"


struct FooItem: public sbe::HashItem
{
    void*   ptr;
    
    inline FooItem( void )
    : ptr(NULL)
    {}
    
    inline ~FooItem( void ) {}
    
    inline FooItem( FooItem const &   item )
    : ptr( item.ptr )
    {}
    
    inline FooItem&   operator=( FooItem const &   item )
    {
        this->ptr = item.ptr;
        return *this;
    }
};

//-------------------------------------------------------//

bool    operator==( FooItem const &  item1, FooItem const &  item2 )
{
    return item1.ptr == item2.ptr;
}

//-------------------------------------------------------//

size_t      hashKey( FooItem const &  item )
{
    return reinterpret_cast<size_t>(item.ptr) >> 2;
}

//---------------------------------------------------------------------------//

static void     test_fooitem( void )
{
    sbe::Hash<FooItem, 1024>    hash;
    
    FooItem     nodes[5000];
    
    for (size_t  i = 0; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        nodes[i].ptr = reinterpret_cast<void*>(i << 2);
        hash.insert( &nodes[i] );
        
        FooItem* item = hash.get( FooItem(nodes[i]) );
        
        SBE_ASSERT( item == &nodes[i] );
    }
    
    for (size_t  i = 0; i < sizeof(nodes)/sizeof(nodes[0]); ++i)
    {
        FooItem* item = hash.get( FooItem(nodes[i]) );
        
        SBE_ASSERT( item == &nodes[i] );
        
        hash.remove( item );
        SBE_ASSERT( hash.get( FooItem(nodes[i]) ) == NULL );
    }
    
    std::cout << "Test: 'test_fooitem' - " << "PASSED" << std::endl;
}

int main( void )
{
    test_fooitem();
    
    return 0;
}
 
