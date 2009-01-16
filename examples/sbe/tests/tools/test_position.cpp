#include <stdlib.h>
#include <iostream>

#include "sbe/debug/debug.hpp"
#include "sbe/tools/position.hpp"

typedef sbe::PositionImpl<size_t>   Position;
typedef sbe::PositionImpl<double>   DoublePosition;

//---------------------------------------------------------------------------//

static void     test_size_t( void )
{
    Position    s1( 100, 20 );
    
    SBE_ASSERT( s1.x() == 100 );
    SBE_ASSERT( s1.y() == 20 );
    
    std::cout << "position: " << s1 << std::endl;
    
    Position    s2( s1 );
    
    SBE_ASSERT( s2.x() == 100 );
    SBE_ASSERT( s2.y() == 20 );
    
    std::cout << "position: " << s2 << std::endl;
    
    Position    s3;
    
    s3 = s1;
    
    SBE_ASSERT( s3.x() == 100 );
    SBE_ASSERT( s3.y() == 20 );
    
    std::cout << "position: " << s3 << std::endl;
    
    s1.setX(0);
    s1.setY(0);
    
    SBE_ASSERT( s1.x() == 0 );
    SBE_ASSERT( s1.y() == 0 );
    
    SBE_ASSERT( s1 != s2 );
    SBE_ASSERT( s2 == s2 );
    
    std::cout << "position: " << s1 << std::endl;
    
    s1 += s2;
    
    SBE_ASSERT( s1 == s2 );
    
    s1 = s2 + s1;
    
    SBE_ASSERT( s1 == (s2 + s3) );
    
    s1 -= s2;
    
    SBE_ASSERT( s1 == ((s2 + s3) - s3) );
    
    
    s1 = Position( 1, 27 );
    s2 = Position( 8, 26 );
    s3 = s1;
    
    SBE_ASSERT( s1 < s2 );
    SBE_ASSERT( s1 <= s2 );
    SBE_ASSERT( s1 <= s3 );
    SBE_ASSERT( s2 > s1 );
    SBE_ASSERT( s2 >= s1 );
    SBE_ASSERT( s1 >= s3 );
}

//---------------------------------------------------------------------------//

static void     test_double( void )
{
    DoublePosition      s1( 100.1, 20.1 );
    
    SBE_ASSERT( sbe::equal( s1.x(), 100.1 ));
    SBE_ASSERT( sbe::equal( s1.y(), 20.1 ));
    
    std::cout << "position: " << s1 << std::endl;
    
    DoublePosition      s2( s1 );
    
    SBE_ASSERT( sbe::equal( s2.x(), 100.1 ));
    SBE_ASSERT( sbe::equal( s2.y(), 20.1 ));
    
    std::cout << "position: " << s2 << std::endl;
    
    DoublePosition      s3;
    
    s3 = s1;
    
    SBE_ASSERT( sbe::equal( s3.x(), 100.1 ));
    SBE_ASSERT( sbe::equal( s3.y(), 20.1 ));
    
    std::cout << "position: " << s3 << std::endl;
    
    s1.setX(0.0);
    s1.setY(0.0);
    
    std::cout << "position: " << s1 << std::endl;
    
    SBE_ASSERT( sbe::equal( s1.x(), 0.0 ));
    SBE_ASSERT( sbe::equal( s1.y(), 0.0 ));
    
    SBE_ASSERT( s1 != s2 );
    SBE_ASSERT( s2 == s2 );
    
    s1 += s2;
    
    SBE_ASSERT( s1 == s2 );
    
    s1 = s2 + s1;
    
    SBE_ASSERT( s1 == (s2 + s3) );
    
    s1 -= s2;
    
    SBE_ASSERT( s1 == ((s2 + s3) - s3) );
}

//---------------------------------------------------------------------------//

int main( void )
{
    test_size_t();
    test_double();
    
    return 0;
}
