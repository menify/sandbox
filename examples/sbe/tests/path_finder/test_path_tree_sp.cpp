#include <stddef.h>
#include <cstdlib>
#include <memory>
#include <iostream>
#include <cstring>
#include <vector>
#include <list>
#include <deque>

#ifdef __GNUG__
    #ifdef TR1
        #include <tr1/memory>
    #endif
#endif

#include "sbe/ut/debug.hpp"
#include "sbe/path_finder/path_tree_sp.hpp"
#include "sbe/tools/position.hpp"
#include "sbe/tools/safe_ptr.hpp"
#include "sbe/tools/auto_ptr.hpp"

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

struct  PathData;
#ifdef TR1
    typedef std::tr1::shared_ptr<PathData>  PathDataPtr;
#else
    typedef sbe::SafePtr<PathData>      PathDataPtr;
#endif

struct  PathData: public sbe::IntrusivePathTree< PathDataPtr >
{
    Position    man_pos;
    Position    box_pos;
    Position    occupy_pos;
    Position    vacant_pos;
    
    inline PathData( void ):    sbe::IntrusivePathTree< PathDataPtr >(), man_pos(), box_pos() {}
    inline ~PathData( void )    {}
};

static void     test( void )
{
    PathDataPtr     path( new PathData );
    
    
    SBE_ASSERT( path->isLast() );
    SBE_ASSERT( path->isRoot() );
    SBE_ASSERT( path->parent() == NULL );
    
    PathDataPtr     child[4];
    
    for (size_t  i = 0; i < 4; ++i)
    {
        child[i].reset( new PathData );
        
        path->attach( i, child[i] );
    }
    
    SBE_ASSERT( !path->isLast() );
    SBE_ASSERT( path->isRoot() );
    SBE_ASSERT( path->parent() == NULL );
    
    for (size_t  i = 0; i < 4; ++i)
    {
        SBE_ASSERT( child[i]->isLast() );
        SBE_ASSERT( !child[i]->isRoot() );
        SBE_ASSERT( child[i]->parent() == path.get() );
    }
    
    //-------------------------------------------------------//
    
    PathDataPtr     grandchild[ 4 ];
    
    for (size_t  i = 0; i < 4; ++i)
    {
        grandchild[i].reset( new PathData );
        
        child[i]->attach( i, grandchild[i] );
        
        SBE_ASSERT( !child[i]->isLast() );
        SBE_ASSERT( grandchild[i]->isLast() );
        SBE_ASSERT( !grandchild[i]->isRoot() );
        SBE_ASSERT( grandchild[i]->parent() == child[i].get() );
    }
    
    //-------------------------------------------------------//
    
    SBE_ASSERT( path->size() == 9 );
    
    for (size_t  i = 0; i < 4; ++i)
    {
        SBE_ASSERT( child[i]->size() == 2 );
        SBE_ASSERT( grandchild[i]->size() == 1 );
    }
    
    //~ path->print();
    
    for (size_t  i = 0; i < 4; ++i)
    {
        grandchild[i]->collapse();
        
        SBE_ASSERT( path->size() == (9 - (i + 1) * 2 ) );
        
        child[i].reset();
        grandchild[i].reset();
    }
    
    SBE_ASSERT( path->isLast() );
    SBE_ASSERT( path->isRoot() );
}

//---------------------------------------------------------------------------//

void    test_2( void )
{
    PathData        path;
    
    for (size_t  i = 0; i < 4; ++i)
    {
        PathDataPtr     child( new PathData );
        
        path.attach( i, child );
        
        for (size_t  k = 0; k < 4; ++k)
        {
            PathDataPtr     grandchild( new PathData );
            
            child->attach( k, grandchild );
        }
    }
    
    SBE_ASSERT( path.size() == 21 );
}

//---------------------------------------------------------------------------//

typedef std::deque<PathDataPtr>    Wave;

void    test_stress( void )
{
    Wave    wave1;
    Wave    wave2;
    
    for (size_t  k = 0; k < 10; ++k)
    {
        PathDataPtr     path( new PathData );
        
        wave1.push_back( path );
        
        for (size_t  n = 0; n < 11; ++n)
        {
            for (Wave::iterator  it = wave1.begin(); it != wave1.end(); ++it)
            {
                for (size_t  i = 0; i < 4; ++i)
                {
                    PathDataPtr     step( new PathData );
                    
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
    //~ test_2();
    
    test_stress();
    
    SBE_ASSERT( s_allocations == 0 );
    
    return 0;
}
