#ifndef SBE_TOOLS_OP_HPP_INCLUDED
#define SBE_TOOLS_OP_HPP_INCLUDED

namespace sbe{

template< typename T>
inline bool    equal( T  a, T  b )     { return a == b; }

template<>
inline bool    equal<float>( float a, float b )
{
    float const     d = a - b;
    return (d > 0) ? (d < 0.00001) : (d > (-0.00001));
}

template<>
inline bool    equal<double>( double a, double b )
{
    double const     d = a - b;
    return (d > 0) ? (d < 0.00001) : (d > (-0.00001));
}

}   // namespace sbe

#endif // SBE_TOOLS_OP_HPP_INCLUDED
