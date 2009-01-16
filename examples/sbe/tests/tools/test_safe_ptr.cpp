
#include <stddef.h>
#include <cstdlib>
#include <ctime>

#include <iostream>
#include <memory>

#include "sbe/debug/debug.hpp"
#include "sbe/tools/safe_ptr.hpp"

using sbe::SafePtr;

//---------------------------------------------------------------------------//

static size_t       s_allocations = 0;

void*   operator new( size_t   size )
{
    void*   ptr = std::malloc( size );
    ++s_allocations;
    
    std::printf("new: %p, size: %u, s_allocations: %u\n", ptr, size, s_allocations );
    
    return ptr;
}

void    operator delete( void * ptr )
{
    if (ptr != NULL)
    {
        --s_allocations;
        std::printf("delete: %p, s_allocations: %u\n", ptr, s_allocations );
        std::free( ptr );
    }
}

//---------------------------------------------------------------------------//

struct  Pos
{
    size_t      x;
    size_t      y;
};

//---------------------------------------------------------------------------//

struct  SharedData
{
    size_t*     count;
    
    inline SharedData( size_t*  in_count ) : count( in_count )  { ++*count; }
    inline ~SharedData( void )  { --*count; }
    
    inline SharedData( SharedData const &  sd )                 : count( sd.count ) { ++*count; }
    inline SharedData&  operator=( SharedData const &  sd )     { count = sd.count; ++*count; return *this; }
};

struct  SharedArrayData
{
    static size_t   count;
    
    inline SharedArrayData( void ) { ++count; }
    inline ~SharedArrayData( void )  { --count; }
};

size_t  SharedArrayData::count = 0;

//-------------------------------------------------------//

void    test_safe_ptr_scope( void )
{
    size_t      count = false;
    size_t      count2 = false;
    
    {
        SafePtr< SharedData >    buf_copy;
        
        {
            SafePtr< SharedData >        buf;
            
            buf = new SharedData( &count );
            
            SBE_ASSERT( count == 1 );
            
            buf_copy = buf;
        }
        
        SBE_ASSERT( count == 1 );
        
        buf_copy = new SharedData( &count2 );
        
        SBE_ASSERT( count == 0 );
        SBE_ASSERT( count2 == 1 );
    }
    
    SBE_ASSERT( count == 0 );
    SBE_ASSERT( count2 == 0 );
}

//---------------------------------------------------------------------------//

void    test_safe_ptr_api( void )
{
    char*               raw_ptr = new char;
    SafePtr<char>       s_ptr( raw_ptr );
    
    SBE_ASSERT( s_ptr == raw_ptr );
    SBE_ASSERT( raw_ptr == s_ptr );
    
    SafePtr<char>       s_ptr_2( s_ptr );
    
    SBE_ASSERT( s_ptr == s_ptr_2 );
    
    SafePtr<char>       s_ptr_3;
    
    SBE_ASSERT( s_ptr_3 == NULL );
    
    s_ptr_3 = s_ptr;
    
    SBE_ASSERT( s_ptr_3 == s_ptr );
    SBE_ASSERT( s_ptr_3.get() == s_ptr.get() );
    
    char*               raw_ptr_another = new char;
    SafePtr<char>       s_ptr_another;
    
    s_ptr_another = raw_ptr_another;
    
    SBE_ASSERT( s_ptr_another == raw_ptr_another );
    
    SBE_ASSERT( &*s_ptr_another == raw_ptr_another );
    SBE_ASSERT( &*(*const_cast<SafePtr<char> const *>(&s_ptr_another)) == raw_ptr_another );
    
    Pos*            raw_foo = new Pos;
    
    raw_foo->x = 3;
    raw_foo->y = 5;
    
    SafePtr<Pos>    foo( raw_foo );
    
    foo->x = 1;
    foo->y = 2;
    
    SBE_ASSERT( raw_foo->x == 1 );
    SBE_ASSERT( raw_foo->y == 2 );
    
    SBE_ASSERT( foo->x == 1 );
    SBE_ASSERT( foo->y == 2 );
    
    SBE_ASSERT( (*const_cast<SafePtr<Pos> const*>(&foo))->x == 1 );
    SBE_ASSERT( (*const_cast<SafePtr<Pos> const*>(&foo))->y == 2 );
    
    char*   buf = new char[16];
    SafePtr<char, sbe::NewArrayDeleter<char> >    safe_buf( buf );
    
    safe_buf[0] = 'a';
    safe_buf[1] = 'b';
    safe_buf[2] = 'c';
    
    SBE_ASSERT( safe_buf[0] == buf[0] );
    SBE_ASSERT( safe_buf[1] == buf[1] );
    SBE_ASSERT( safe_buf[2] == buf[2] );
    
    SafePtr<char, sbe::NewArrayDeleter<char> > const&   const_safe_buf = safe_buf;
    
    SBE_ASSERT( const_safe_buf[0] == safe_buf[0] );
    SBE_ASSERT( const_safe_buf[1] == safe_buf[1] );
    SBE_ASSERT( const_safe_buf[2] == safe_buf[2] );
    
    SBE_ASSERT( !(!const_safe_buf) );
    
    s_ptr = NULL;
    SBE_ASSERT( !s_ptr );
    
    SBE_ASSERT( s_ptr_2 != buf );
    SBE_ASSERT( buf != s_ptr_2  );
    SBE_ASSERT( s_ptr != s_ptr_2 );
    
    
    char        pool[100];
    
    SafePtr<char, sbe::PlacementNewDeleter<char> >      p1( new( pool )    char );
    SafePtr<char, sbe::PlacementNewDeleter<char> >      p2( new( pool + 1) char );
    
    SBE_ASSERT( p1 < p2 );
    SBE_ASSERT( p1 < &*p2 );
    SBE_ASSERT( &*p1 < p2 );
    
    SBE_ASSERT( p1 <= p2 );
    SBE_ASSERT( p1 <= &*p2 );
    SBE_ASSERT( &*p1 <= p2 );
    
    SBE_ASSERT( p1 <= p1 );
    SBE_ASSERT( p1 <= &*p1 );
    SBE_ASSERT( &*p1 <= p1 );
    
    SBE_ASSERT( p2 > p1 );
    SBE_ASSERT( p2 > &*p1 );
    SBE_ASSERT( &*p2 > p1 );
    
    SBE_ASSERT( p2 >= p1 );
    SBE_ASSERT( p2 >= &*p1 );
    SBE_ASSERT( &*p2 >= p1 );
    
    SBE_ASSERT( p2 >= p2 );
    SBE_ASSERT( p2 >= &*p2 );
    SBE_ASSERT( &*p2 >= p2 );
    
    std::cout << "foo: " << foo << std::endl;
    std::cout << "p1: " << p1 << std::endl;
    std::cout << "p2: " << p2 << std::endl;
    
    //-------------------------------------------------------//
    
    SafePtr<char>   owner1( new char );
    SafePtr<char>   owner2( new char );
    
    owner1 = owner2;
    
    owner1 = new char;
    
    //-------------------------------------------------------//
    
    char*           same_p = new char;
    SafePtr<char>   ssame_p( same_p );
    
    ssame_p = same_p;       // assign twice the same pointer
    
    //-------------------------------------------------------//
    
    SafePtr<char>   ssame_p1( new char );
    SafePtr<char>   ssame_p2( ssame_p1 );
    
    ssame_p1 = ssame_p2;       // assign twice the same pointer
    
    //-------------------------------------------------------//
    
    #if 0
        char*   bad_assigned_ptr = new char;
        ssame_p1 = bad_assigned_ptr;
        ssame_p2 = bad_assigned_ptr;
        
        ssame_p1 = ssame_p2; // must be assert!
    #endif
}

//---------------------------------------------------------------------------//

void    test_scope_stress( void )
{
    size_t      count = false;
    size_t      count2 = false;
    
    {
        SafePtr< SharedData >      shared_data( new SharedData( &count ) );
        SafePtr< SharedData >      shared_data2( new SharedData( &count2 ) );
        
        SBE_ASSERT( count == 1);
        SBE_ASSERT( count2 == 1 );
        
        {
            SafePtr< SharedData >      safe_ptrs[ 500 ];
            
            for (size_t k = 0; k < 500; ++k)
            {
                for (size_t  i = 0; i < sizeof(safe_ptrs)/sizeof(safe_ptrs[0]); ++i)
                {
                    if (std::rand() & 0x01)
                    {
                        safe_ptrs[i] = shared_data;
                    }
                    else
                    {
                        safe_ptrs[i] = shared_data2;
                    }
                }
            }
            
            SBE_ASSERT( count == 1 );
            SBE_ASSERT( count2 == 1 );
        }
        
        SBE_ASSERT( count == 1 );
        SBE_ASSERT( count2 == 1 );
    }
    
    SBE_ASSERT( count == 0 );
    SBE_ASSERT( count2 == 0 );
}

//---------------------------------------------------------------------------//

void    test_deleters( void )
{
    size_t      count = 0;
    
    //-------------------------------------------------------//
    // new
    {
        SafePtr< SharedData >       new_ptr( new SharedData( &count ) );
        SBE_ASSERT( count == 1 );
    }
    SBE_ASSERT( count == 0 );
    
    //-------------------------------------------------------//
    // new[]
    {
        SBE_ASSERT( SharedArrayData::count == 0 );
        
        SafePtr< SharedArrayData, sbe::NewArrayDeleter<SharedArrayData> >     new_array_ptr( new SharedArrayData[20] );
        
        SBE_ASSERT( SharedArrayData::count == 20 );
    }
    SBE_ASSERT( SharedArrayData::count == 0 );
    
    //-------------------------------------------------------//
    // placement new
    {
        size_t      pool[ (sizeof(SharedData) + (sizeof(size_t) - 1)) / sizeof(size_t) ];
        
        SharedData*     raw_ptr = new(&pool) SharedData( &count );
        
        SafePtr< SharedData, sbe::PlacementNewDeleter<SharedData> >     new_ptr;
        
        new_ptr = raw_ptr;
        
        SBE_ASSERT( count == 1 );
    }
    SBE_ASSERT( count == 0 );
}

//---------------------------------------------------------------------------//

int main( void )
{
    std::srand( static_cast<unsigned int>( std::clock() ) );
    
    SBE_ASSERT( s_allocations == 0 );
    
    test_safe_ptr_api();
    
    SBE_ASSERT( s_allocations == 0 );
    
    test_safe_ptr_scope();
    
    SBE_ASSERT( s_allocations == 0 );
    
    test_scope_stress();
    
    SBE_ASSERT( s_allocations == 0 );
    
    test_deleters();
    
    SBE_ASSERT( s_allocations == 0 );
    
    return 0;
}
 
