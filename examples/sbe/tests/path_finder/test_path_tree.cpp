
#include <stddef.h>
#include <cstdlib>
#include <iostream>
#include <vector>
#include <list>
#include <deque>

#include "sbe/debug/debug.hpp"
#include "sbe/tools/position.hpp"
#include "sbe/path_finder/path_tree.hpp"


//---------------------------------------------------------------------------//

#ifdef SBE_DEBUG

static size_t       s_allocations = 0;      //lint !e956    // Note -- Non const, non volatile static or external variable

void*   operator new( size_t   size )       //lint -e{1771} -e{1921}    // Info -- function 'operator new(unsigned long)' replaces global function
{
    void* const     ptr = std::malloc( size );
    ++s_allocations;
    
    //~ std::printf("new: %p, size: %u, s_allocations: %u\n", ptr, size, s_allocations );
    
    return ptr;
}

void    operator delete( void * ptr )       //lint -e{1771} -e{1921}    // Info -- function 'operator new(unsigned long)' replaces global function
{
    if (ptr != NULL)
    {
        --s_allocations;
        std::free( ptr );
        
        //~ std::printf("delete: %p, s_allocations: %u\n", ptr, s_allocations );
    }
}
#endif  // #ifdef SBE_DEBUG

//---------------------------------------------------------------------------//

typedef sbe::PositionImpl<size_t>    Position;

struct  PathData
{
    Position    man_pos;
    Position    box_pos;
    Position    occupy_pos;
    Position    vacant_pos;
};

typedef sbe::PathTree< PathData >    Path;

#ifndef SBE_PATH_TREE_STRESS_TEST
static void     test( void )
{
    Path            path;
    
    SBE_ASSERT( path.size() == 0 );
    
    Path::iterator const    head = path.attach( PathData() );
    
    SBE_ASSERT( head.isLast() );
    SBE_ASSERT( path.size() == 1 );
    
    Path::iterator  child[4];
    
    for (size_t  i = 0; i < 4; ++i)
    {
        child[i] = path.attach( PathData(), head, i );
        SBE_ASSERT( child[i].isLast() );
    }
    
    SBE_ASSERT( path.size() == 5 );
    
    //-------------------------------------------------------//
    
    Path::iterator      grandchild[ 4 ];
    
    for (size_t  i = 0; i < 4; ++i)
    {
        grandchild[i] = path.attach( PathData(), child[i], i );
        
        SBE_ASSERT( !child[i].isLast() );
        SBE_ASSERT( grandchild[i].isLast() );
        SBE_ASSERT( child[i].size() == 2 );
        SBE_ASSERT( grandchild[i].size() == 1 );
    }
    
    //-------------------------------------------------------//
    
    SBE_ASSERT( path.size() == 9 );
    
    #ifdef SBE_DEBUG
        path.print();
    #endif
    
    for (size_t  i = 0; i < 3; ++i)
    {
        path.collapse( grandchild[i] );
        
        SBE_ASSERT( path.size() == (9 - (i + 1) * 2 ) );
    }
    
    path.collapse( grandchild[3] );
    
    SBE_ASSERT( path.size() == 0 );
}
#endif  // #ifndef SBE_PATH_TREE_STRESS_TEST

//---------------------------------------------------------------------------//

#ifndef SBE_PATH_TREE_STRESS_TEST
static void    test_2( void )
{
    Path        path;
    
    Path::iterator const    head = path.attach( PathData() );
    
    for (size_t  i = 0; i < 4; ++i)
    {
        Path::iterator const  child = path.attach( PathData(), head, i );
        
        for (size_t  k = 0; k < 4; ++k)
        {
            (void)path.attach( PathData(), child, k );
        }
    }
    
    #ifdef SBE_DEBUG
    path.print();
    #endif
    
    SBE_ASSERT( path.size() == 21 );
}
#endif  // #ifndef SBE_PATH_TREE_STRESS_TEST

//---------------------------------------------------------------------------//

#ifdef SBE_PATH_TREE_STRESS_TEST
static void    test_stress( void )
{
    typedef std::vector<Path::iterator>     Wave;
    
    Wave    wave1;
    Wave    wave2;
    
    for (size_t  k = 0; k < 3; ++k)
    {
        Path    path;
        
        wave1.push_back( path.attach( PathData() ) );
        
        for (size_t  n = 0; n < 11; ++n)
        {
            for (Wave::iterator  it = wave1.begin(); it != wave1.end(); ++it)
            {
                for (size_t  i = 0; i < 4; ++i)
                {
                    wave2.push_back( path.attach( PathData(), *it, i ) );
                }
            }
            
            wave1.clear();
            wave1.swap( wave2 );
        }
        
        wave1.clear();
    }
}
#endif  // #ifdef SBE_PATH_TREE_STRESS_TEST

//---------------------------------------------------------------------------//

int main( void )
{
    #ifndef SBE_PATH_TREE_STRESS_TEST
        test();
        test_2();
    #else
        test_stress();
    #endif
    
    
    PathData    data;
    
    static_cast<void>(data);
    static_cast<void>(data.man_pos);
    static_cast<void>(data.box_pos);
    static_cast<void>(data.occupy_pos);
    static_cast<void>(data.vacant_pos);
    
    SBE_ASSERT( s_allocations == 0 );
    
    return 0;
}
