
#include <iostream>

#include "sbe/allocators/fixed_allocator.hpp"

//---------------------------------------------------------------------------//

static void     test_char( void )
{
    char        buf[10];
    char*       ptr[3];
    
    sbe::FixedAllocator<char,1>       alloc( buf, sizeof(buf) );
    
    for (size_t  i = 0; i < 3; ++i)
    {
        ptr[i] = alloc.allocate();
    }
    
    SBE_ASSERT( ptr[0] != NULL );
    SBE_ASSERT( ptr[1] != NULL );
    SBE_ASSERT( ptr[2] == NULL );
    
    alloc.deallocate( NULL );
    
    for (size_t  i = 0; i < 3; ++i)
    {
        alloc.deallocate( ptr[i] );
    }
    
    SBE_ASSERT( alloc.test() );
    
    std::cout << "Test: 'test_char' - " << "PASSED" << std::endl;
}

struct Foo
{
    void*   ptr;
    size_t  size;
    size_t  offset;
    size_t  reserved1;
    size_t  reserved2;
};


static void     test_foo( void )
{
    char                        tiny_buf[sizeof(Foo) - 1];
    sbe::FixedAllocator<Foo>    tiny_alloc( tiny_buf, sizeof(tiny_buf) );
    
    SBE_ASSERT( tiny_alloc.allocate() == NULL );
    
    //-------------------------------------------------------//
    
    char                        buf[sizeof(Foo) * 3 + 4];
    sbe::FixedAllocator<Foo>    alloc( buf, sizeof(buf) );
    
    Foo*       ptr[3];
    
    for (size_t  i = 0; i < 3; ++i)
    {
        ptr[i] = alloc.allocate();
        SBE_ASSERT( ptr[i] != NULL );
    }
    
    SBE_ASSERT( alloc.allocate() == NULL );
    
    for (size_t  i = 0; i < 3; ++i)
    {
        alloc.deallocate( ptr[i] );
    }
    
    SBE_ASSERT( alloc.test() );
    
    std::cout << "Test: 'test_foo' - " << "PASSED" << std::endl;
}

static void     test_many( void )
{
    char                            buf[10000];
    sbe::FixedAllocator<double>     alloc( buf, sizeof(buf) );
    
    double*     ptr[10000];
    
    for (size_t  i = 0; i < sizeof(ptr) / sizeof(ptr[0]); ++i)
    {
        ptr[i] = alloc.allocate();
        if (i & 0x1)
        {
            alloc.deallocate( ptr[i-1] );
            ptr[i-1] = NULL;
        }
    }
    
    for (size_t  i = 0; i < sizeof(ptr) / sizeof(ptr[0]); ++i)
    {
        alloc.deallocate( ptr[i] );
    }
    
    SBE_ASSERT( alloc.test() );
    
    std::cout << "Test: 'test_many' - " << "PASSED" << std::endl;
}

//---------------------------------------------------------------------------//

int main( void )
{
    test_char();
    test_foo();
    test_many();
    
    return 0;
}
