
#include <stddef.h>
#include <cstdlib>
#include <memory>
#include <iostream>

#include "sbe/debug/debug.hpp"
#include "sbe/tools/size.hpp"

#include "sbe/tools/auto_ptr.hpp"

typedef sbe::SizeImpl<size_t>   Size;
typedef sbe::SizeImpl<double>   DoubleSize;

//---------------------------------------------------------------------------//

static void     test_size_t( void )
{
    Size    s1( 100, 20);
    
    SBE_ASSERT( s1.width() == 100 );
    SBE_ASSERT( s1.height() == 20 );
    
    std::cout << "size: " << s1 << std::endl;
    
    Size    s2( s1 );
    
    SBE_ASSERT( s2.width() == 100 );
    SBE_ASSERT( s2.height() == 20 );
    
    std::cout << "size: " << s2 << std::endl;
    
    Size    s3;
    
    s3 = s1;
    
    SBE_ASSERT( s3.width() == 100 );
    SBE_ASSERT( s3.height() == 20 );
    
    std::cout << "size: " << s3 << std::endl;
    
    s1.setWidth(0);
    s1.setHeight(0);
    
    SBE_ASSERT( s1.width() == 0 );
    SBE_ASSERT( s1.height() == 0 );
    
    SBE_ASSERT( s1 != s2 );
    SBE_ASSERT( s2 == s2 );
    
    std::cout << "size: " << s1 << std::endl;
}

//---------------------------------------------------------------------------//

static void     test_double( void )
{
    DoubleSize      s1( 100.1, 20.1 );
    
    SBE_ASSERT( sbe::equal( s1.width(), 100.1 ) );
    SBE_ASSERT( sbe::equal( s1.height(), 20.1 ) );
    
    std::cout << "size: " << s1 << std::endl;
    
    DoubleSize      s2( s1 );
    
    SBE_ASSERT( sbe::equal( s2.width(), 100.1 ));
    SBE_ASSERT( sbe::equal( s2.height(), 20.1 ));
    
    std::cout << "size: " << s2 << std::endl;
    
    DoubleSize      s3;
    
    s3 = s1;
    
    SBE_ASSERT( sbe::equal( s3.width(), 100.1) );
    SBE_ASSERT( sbe::equal( s3.height(), 20.1) );
    
    std::cout << "size: " << s3 << std::endl;
    
    s1.setWidth(0.1);
    s1.setHeight(0.1);
    
    std::cout << "size: " << s1 << std::endl;
    
    SBE_ASSERT( sbe::equal( s1.width(), 0.1) );
    SBE_ASSERT( sbe::equal( s1.height(), 0.1) );
    
    SBE_ASSERT( s1 != s2 );
    SBE_ASSERT( s2 == s2 );
}

//---------------------------------------------------------------------------//

int main( void )
{
    test_size_t();
    test_double();
    
    return 0;
}
