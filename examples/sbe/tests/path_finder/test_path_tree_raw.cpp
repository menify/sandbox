#include <stddef.h>
#include <cstdlib>
#include <memory>
#include <iostream>
#include <vector>
#include <list>
#include <deque>

#include "sbe/ut/debug.hpp"
#include "sbe/path_finder/path_tree_raw.hpp"
#include "sbe/tools/position.hpp"
#include "sbe/tools/auto_ptr.hpp"
#include "sbe/tools/safe_ptr.hpp"

//---------------------------------------------------------------------------//

static size_t       s_allocations = 0;

void*   operator new( size_t   size )
{
    void*   ptr = std::malloc( size );
    ++s_allocations;
    
    //~ std::printf("new: %p, size: %u, s_allocations: %u\n", ptr, size, s_allocations );
    
    return ptr;
}

void    operator delete( void * ptr )
{
    if (ptr != NULL)
    {
        --s_allocations;
        std::free( ptr );
        
        //~ std::printf("delete: %p, s_allocations: %u\n", ptr, s_allocations );
    }
}

//---------------------------------------------------------------------------//

typedef sbe::PositionImpl<size_t>    Position;

struct  PathData: public sbe::IntrusivePathTree<PathData>
{
    Position    man_pos;
    Position    box_pos;
    Position    occupy_pos;
    Position    vacant_pos;
    
    inline PathData( void ):    sbe::IntrusivePathTree<PathData>(), man_pos(), box_pos() {}
    inline ~PathData( void )    {}
};

static void     test( void )
{
    sbe::AutoPtr<PathData>    path( new PathData );
    
    SBE_ASSERT( path->isLast() );
    SBE_ASSERT( path->isRoot() );
    SBE_ASSERT( path->parent() == NULL );
    SBE_ASSERT( const_cast<PathData const*>(&*path)->parent() == NULL );
    
    PathData*       child[4];
    
    for (size_t  i = 0; i < 4; ++i)
    {
        child[i] = path->attach( i );
    }
    
    SBE_ASSERT( !path->isLast() );
    SBE_ASSERT( path->isRoot() );
    SBE_ASSERT( path->parent() == NULL );
    
    for (size_t  i = 0; i < 4; ++i)
    {
        SBE_ASSERT( child[i]->isLast() );
        SBE_ASSERT( !child[i]->isRoot() );
        SBE_ASSERT( child[i]->parent() == path );
    }
    
    PathData*       grandchild[ 4 ];
    
    for (size_t  i = 0; i < 4; ++i)
    {
        grandchild[i] = child[i]->attach(3 - i);
        
        SBE_ASSERT( !child[i]->isLast() );
        SBE_ASSERT( grandchild[i]->isLast() );
        SBE_ASSERT( !grandchild[i]->isRoot() );
        SBE_ASSERT( grandchild[i]->parent() == child[i] );
    }
    
    for (size_t  i = 1; i < 4; ++i)
    {
        delete child[ i ];
        
        SBE_ASSERT( !path->isLast() );
    }
    
    grandchild[0]->collapse();
    
    SBE_ASSERT( path->isLast() );
    SBE_ASSERT( path->isRoot() );
    
    SBE_ASSERT( s_allocations == 1 );
}

//---------------------------------------------------------------------------//

typedef std::deque<PathData*>    Wave;

void    test_stress( void )
{
    Wave    wave1;
    Wave    wave2;
    
    for (size_t  k = 0; k < 10; ++k)
    {
        PathData     path;
        
        wave1.push_back( &path );
        
        for (size_t  n = 0; n < 11; ++n)
        {
            for (Wave::iterator  it = wave1.begin(); it != wave1.end(); ++it)
            {
                for (size_t  i = 0; i < 4; ++i)
                {
                    PathData*     step( new PathData );
                    
                    (*it)->attach( i, step );
                    
                    wave2.push_back( step );
                }
            }
            
            wave1.clear();
            wave1.swap( wave2 );
        }
        
        wave1.clear();
    }
}

//---------------------------------------------------------------------------//

int main( void )
{
    //~ test();
    
    test_stress();
    
    SBE_ASSERT( s_allocations == 0 );
    
    return 0;
}
