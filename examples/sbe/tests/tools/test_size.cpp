
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

template <typename T, size_t  maxSize>
class MovingAverage
{
public:
    explicit inline MovingAverage( size_t  size = maxSize )
    : _start(0)
    , _size(size)
    , _actualSize(0)
    , _avg()
    {}
    
    inline ~MovingAverage()
    {}
    
    
    void    append( T  val )
    {
        SBE_ASSERT(_actualSize <= _size);
        
        const size_t    valuePos = (_start + _actualSize) % maxSize;
        
        if (_actualSize == _size) {
            _avg += val - _values[_start];
            _start = (_start + 1) % maxSize;
        
        } else {
            if (_actualSize > 0) {
                _avg += val;
            } else {
                _avg = val;
            }
            
            ++_actualSize;
        }
        
        _values[valuePos] = val;
    }
    
    void    setSize(size_t  size)
    {
        if (size > maxSize) {
            size = maxSize;
        
        } else if (size == 0) {
            size = 1;
        }
        
        for (; _actualSize > size; --_actualSize) {
            _avg -= _values[_start];
            _start = (_start + 1) % maxSize;
        }
        
        _size = size;
    }
    
    T   value()
    {
        SBE_ASSERT(_actualSize > 0);
        return _avg / static_cast<T>(_actualSize);
    }
    
    void    reset()
    {
        _actualSize = 0;
    }

private:
    size_t  _start;
    size_t  _size;
    size_t  _actualSize;
    T       _avg;
    T       _values[maxSize];
};

static void     test_mva()
{
    MovingAverage<size_t,32>    avg(4);
    
    static size_t const  values[]       = {1,2,3,4,5,5,4,1,3,5};
    static size_t const  avg4_values[]  = {1,1,2,2,3,4,4,3,3,3};
    
    for (size_t  i = 0; i < sizeof(values) / sizeof(values[0]); ++i)
    {
        avg.append( values[i] );
        SBE_ASSERT( avg.value() == avg4_values[i] );
    }
    
    avg.setSize(2);
    SBE_ASSERT( avg.value() == 4 );
    avg.setSize(3);
    SBE_ASSERT( avg.value() == 4 );
    avg.setSize(5);
    SBE_ASSERT( avg.value() == 4 );
    avg.setSize(2);
    SBE_ASSERT( avg.value() == 4 );
    
    static size_t const  avg2_values[]   = {3,1,2,3,4,5,4,2,2,4};
    
    for (size_t  i = 0; i < sizeof(values) / sizeof(values[0]); ++i)
    {
        avg.append( values[i] );
        SBE_ASSERT( avg.value() == avg2_values[i] );
    }
    
    avg.setSize(5);
    static size_t const  avg5_values[]   = {3,2,2,3,3,3,4,3,3,3};
    
    for (size_t  i = 0; i < sizeof(values) / sizeof(values[0]); ++i)
    {
        avg.append( values[i] );
        SBE_ASSERT( avg.value() == avg5_values[i] );
    }
    
    avg.reset();
    
    static size_t const  avg5_values2[]   = {1,1,2,2,3,3,4,3,3,3};
    
    for (size_t  i = 0; i < sizeof(values) / sizeof(values[0]); ++i)
    {
        avg.append( values[i] );
        SBE_ASSERT( avg.value() == avg5_values2[i] );
    }
}


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
    
    test_mva();
    
    return 0;
}
