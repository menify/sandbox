#ifndef SBE_POSITION_HPP_INCLUDED
#define SBE_POSITION_HPP_INCLUDED

#include <ostream>

#include "sbe/tools/op.hpp"

namespace sbe{

//---------------------------------------------------------------------------//

template <typename T>
class   PositionImpl
{
    T       x_;
    T       y_;
    
    typedef PositionImpl<T>     ThisType;
    
public:
    
    inline  ~PositionImpl( void )   {}
    inline  PositionImpl( void )                    : x_(), y_() {}
    inline  PositionImpl( T  in_x, T  in_y )        : x_( in_x ) , y_( in_y ) {}
    inline  PositionImpl( ThisType const &  pos )   : x_( pos.x_ ) , y_( pos.y_ ) {}
    
    inline ThisType&    operator=( ThisType const & pos )   { this->x_ = pos.x_; this->y_ = pos.y_; return *this; }
    inline ThisType&    operator+=( ThisType const & pos )  { this->x_ += pos.x_; this->y_ += pos.y_; return *this; }
    inline ThisType&    operator-=( ThisType const & pos )  { this->x_ -= pos.x_; this->y_ -= pos.y_; return *this; }
    inline ThisType     operator-( void )                   { return ThisType( -this->x_, -this->y_ ); }
    inline ThisType     operator+( void )                   { return ThisType( this->x_, this->y_ ); }
    
    inline T            x( void ) const     { return this->x_; }
    inline T            y( void ) const     { return this->y_; }
    
    inline void         setX( T  in_x )    { this->x_ = in_x; }
    inline void         setY( T  in_y )    { this->y_ = in_y; }
    
    //lint --e{1727}    // not previously defined inline
    friend inline ThisType  operator +( ThisType const &  pos1, ThisType const &  pos2 )    { return ThisType( pos1.x_ + pos2.x_, pos1.y_ + pos2.y_ ); }
    friend inline ThisType  operator -( ThisType const &  pos1, ThisType const &  pos2 )    { return ThisType( pos1.x_ - pos2.x_, pos1.y_ - pos2.y_ ); }
    friend inline bool      operator ==( ThisType const &  pos1, ThisType const &  pos2 )   { return equal(pos1.x_, pos2.x_) && equal(pos1.y_, pos2.y_); }
    friend inline bool      operator !=( ThisType const &  pos1, ThisType const &  pos2 )   { return !(pos1 == pos2); }
    
    friend inline bool      operator <( ThisType const &  pos1, ThisType const &  pos2 )    { return (pos1.x_ * pos1.x_ + pos1.y_ * pos1.y_) < (pos2.x_ * pos2.x_ + pos2.y_ * pos2.y_); }
    friend inline bool      operator <=( ThisType const &  pos1, ThisType const &  pos2 )   { return !(pos2 < pos1); }
    friend inline bool      operator >( ThisType const &  pos1, ThisType const &  pos2 )    { return (pos2 < pos1); }
    friend inline bool      operator >=( ThisType const &  pos1, ThisType const &  pos2 )   { return !(pos1 < pos2); }
};

//---------------------------------------------------------------------------//

template<typename T, typename CharT, typename Traits >
inline std::basic_ostream< CharT, Traits>& operator<< (
    
    std::basic_ostream<CharT, Traits>&  os,
    PositionImpl<T> const &             pos
)
//lint -e{1929}   // Note -- function returning a reference
{
    return os << pos.x() << ", " << pos.y();
}

//---------------------------------------------------------------------------//

}   // namespace sbe

#endif  //  #ifndef SBE_POSITION_HPP_INCLUDED
