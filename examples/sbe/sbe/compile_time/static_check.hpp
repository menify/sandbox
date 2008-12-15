#ifndef SBE_STATIC_CHECK_HPP_INCLUDED
#define SBE_STATIC_CHECK_HPP_INCLUDED

namespace sbe{

template <typename T, typename U>
class   CheckConversion
{
    typedef char    Possible;
    class Impossible { Possible[2]; }
    
    Possible        check(U);
    Impossible      check(...);
    T               makeT();
    
public:
    enum    { possible = (sizeof(check( makeT() ) ) == sizeof(Possible)) };
}

}   // namespace sbe

#endif  // #ifndef SBE_STATIC_CHECK_HPP_INCLUDED
