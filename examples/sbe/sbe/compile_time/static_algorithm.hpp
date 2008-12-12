#ifndef SBE_STATIC_ALGORITHM_HPP_INCLUDED
#define SBE_STATIC_ALGORITHM_HPP_INCLUDED

namespace sbe {

template <unsigned long  size1, unsigned long  size2, bool return_first >
struct StaticMinMaxHelper
{
    enum { result = size1 };
};

template <unsigned long  size1, unsigned long  size2>
struct StaticMinMaxHelper< size1, size2, false >
{
    enum { result = size2 };
};

//---------------------------------------------------------------------------//

template <unsigned long  size1, unsigned long  size2>
struct StaticMin
{
    enum { result = StaticMinMaxHelper< size1, size2, (size1 < size2) >::result };
};

//---------------------------------------------------------------------------//

template <unsigned long  size1, unsigned long  size2>
struct StaticMax
{
    enum { result = StaticMinMaxHelper< size1, size2, (size1 > size2) >::result };
};

}   // namespace sbe

#endif  // #ifndef SBE_STATIC_ALGORITHM_HPP_INCLUDED
