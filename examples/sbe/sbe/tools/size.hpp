#ifndef SBE_SIZE_HPP_INCLUDED
#define SBE_SIZE_HPP_INCLUDED

#include <iostream>

#include "sbe/tools/op.hpp"

namespace sbe{

//---------------------------------------------------------------------------//

template <typename T>
class   SizeImpl
{
    T       width_;
    T       height_;
    
    typedef SizeImpl<T>     ThisType;
    
    //-------------------------------------------------------//
    
public:
    
    inline  ~SizeImpl( void )   {}
    inline  SizeImpl( void )                    : width_(), height_() {}
    inline  SizeImpl( T  w, T  h )              : width_( w ), height_( h ) {}
    inline  SizeImpl( ThisType const &  pos )   : width_( pos.width_ ), height_( pos.height_ ) {}
    
    inline ThisType&   operator=( ThisType const & pos )    { this->width_ = pos.width_;  this->height_ = pos.height_;  return *this; }
    
    inline T            width( void ) const { return this->width_; }
    inline T            height( void ) const { return this->height_; }
    
    inline void         setWidth( T  w )        { this->width_ = w; }
    inline void         setHeight( T  h )       { this->height_ = h; }
    
    friend inline bool  operator ==( ThisType const &  pos1, ThisType const &  pos2 )   { return equal(pos1.width_, pos2.width_) && equal(pos1.height_, pos2.height_); }
    friend inline bool  operator !=( ThisType const &  pos1, ThisType const &  pos2 )   { return !(pos1 == pos2); }
};

//---------------------------------------------------------------------------//

template<typename T, typename CharT, typename Traits >
inline std::basic_ostream< CharT, Traits>& operator<< (
    
    std::basic_ostream<CharT, Traits>&  os,
    SizeImpl<T> const &                 size
)
{
    return os << size.width() << ", " << size.height();
}

//---------------------------------------------------------------------------//

}   // namespace sbe

#endif  //  #ifndef SBE_SIZE_HPP_INCLUDED
