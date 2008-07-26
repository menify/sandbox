#ifndef SBE_AUTO_PTR_HPP_INCLUDED
#define SBE_AUTO_PTR_HPP_INCLUDED

#include "sbe/ut/debug.hpp"
#include "sbe/tools/deleters.hpp"

namespace sbe{

//---------------------------------------------------------------------------//

/*
    Class: AutoPtr
    This is similar to std::auto_ptr, but it has an optional delete strategy parameter.
    By default it uses operator 'delete' to delete a object.
    But it's possible to override a delete strategy.
    
    Parameters:
        T           - a type which is being pointed to
        TDeleter    - a functor, which is used to destroy an object
    
    See also:
        <Deleters>
*/
template <typename T, class  TDeleter = NewDeleter<T> >
class AutoPtr
{
public:
    typedef T   element_type;
    
private:
    typedef AutoPtr<T, TDeleter>        ThisType;
    
    T*  ptr_;
    
    inline void     deletePtr( void )       { TDeleter()( this->ptr_ ); }
    
public:
    
    // constructor: AutoPtr( T*  p = NULL )
    // A default constructor.
    // A pointer points to NULL.
    explicit inline AutoPtr( T*  p = NULL )     : ptr_( p ) {}
    
    // constructor: AutoPtr( AutoPtr&  auto_ptr )
    // A copy constructor.
    // A copied pointer transmits ownership to the new pointer.
    inline AutoPtr( AutoPtr&  auto_ptr )        : ptr_( auto_ptr.release() )  {}
    inline ~AutoPtr( void )                     { this->deletePtr(); }
    
    // operator: AutoPtr& operator=( AutoPtr&  auto_ptr)
    // A copy operator.
    // The current owned object is destroyed.
    // A copied pointer transfers ownership to the new pointer.
    AutoPtr& operator=( AutoPtr&  auto_ptr)         { this->reset( auto_ptr ); return *this; }
    
    // operator: AutoPtr& operator=( T*  ptr )
    // Assignment operator.
    // The current owned object is destroyed.
    // And the ownership transfers to the new pointer.
    AutoPtr& operator=( T*  ptr )                   { this->reset( ptr ); return *this; }
    
    // method: T*  get( void )
    // Returns the current value of the owned pointer.
    inline T*           get( void )                 { return this->ptr_; }
    inline T const*     get( void ) const           { return this->ptr_; }
    
    // method: void    reset( T*  ptr )
    // Changes the currently owned object to the new one.
    // The previously owned object is destroyed.
    inline void         reset( T*  ptr = NULL )     { if (ptr != this->ptr_) { this->deletePtr(); this->ptr_ = ptr; } }
    inline void         reset( AutoPtr&  auto_ptr ) { SBE_ASSERT( (auto_ptr.ptr_ != this->ptr_) || (this->ptr_ == NULL) ); this->reset( auto_ptr.release() ); }
    
    // method: T*   release( void )
    // Releases the ownership of object.
    // Returs the pointer to unmanaged object.
    inline T*           release( void )             { T*  ptr; ptr = this->ptr_; this->ptr_ = NULL; return ptr; }
    
    inline T&           operator*( void )           { SBE_ASSERT( this->ptr_ != NULL ); return *this->ptr_; }
    inline T const&     operator*( void )  const    { SBE_ASSERT( this->ptr_ != NULL ); return *this->ptr_; }
    
    inline T*           operator->( void )          { SBE_ASSERT( this->ptr_ != NULL ); return this->ptr_; }
    inline T const*     operator->( void )  const   { SBE_ASSERT( this->ptr_ != NULL ); return this->ptr_; }
    
    inline T&           operator []( unsigned long  index )         { SBE_ASSERT( this->ptr_ != NULL ); return this->ptr_[ index ]; }
    inline T const&     operator []( unsigned long  index ) const   { SBE_ASSERT( this->ptr_ != NULL ); return this->ptr_[ index ]; }
    
    inline bool         operator !( void )   const                              { return this->ptr_ == NULL; }
    
    inline friend bool  operator ==( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ == p2.ptr_; }
    inline friend bool  operator ==( ThisType const&  p1, T const*  p2)         { return p1.ptr_ == p2; }
    inline friend bool  operator ==( T const*  p2, ThisType const&  p1)         { return p1.ptr_ == p2; }
    
    inline friend bool  operator !=( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ != p2.ptr_; }
    inline friend bool  operator !=( ThisType const&  p1, T const*  p2)         { return p1.ptr_ != p2; }
    inline friend bool  operator !=( T const*  p2, ThisType const&  p1)         { return p1.ptr_ != p2; }
    
    inline friend bool  operator <( ThisType const&  p1, ThisType const&  p2)   { return p1.ptr_ < p2.ptr_; }
    inline friend bool  operator <( ThisType const&  p1, T const*  p2)          { return p1.ptr_ < p2; }
    inline friend bool  operator <( T const*  p2, ThisType const&  p1)          { return p2 < p1.ptr_; }
    
    inline friend bool  operator <=( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ <= p2.ptr_; }
    inline friend bool  operator <=( ThisType const&  p1, T const*  p2)         { return p1.ptr_ <= p2; }
    inline friend bool  operator <=( T const*  p2, ThisType const&  p1)         { return p2 <= p1.ptr_; }
    
    inline friend bool  operator >( ThisType const&  p1, ThisType const&  p2)   { return p1.ptr_ > p2.ptr_; }
    inline friend bool  operator >( ThisType const&  p1, T const*  p2)          { return p1.ptr_ > p2; }
    inline friend bool  operator >( T const*  p2, ThisType const&  p1)          { return p2 > p1.ptr_; }
    
    inline friend bool  operator >=( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ >= p2.ptr_; }
    inline friend bool  operator >=( ThisType const&  p1, T const*  p2)         { return p1.ptr_ >= p2; }
    inline friend bool  operator >=( T const*  p2, ThisType const&  p1)         { return p2 >= p1.ptr_; }
};

template<typename T, class TDeleter, typename CharT, typename Traits >
inline std::basic_ostream< CharT, Traits>& operator<< (
    
    std::basic_ostream<CharT, Traits>&      os,
    AutoPtr<T,TDeleter> const &             auto_ptr
)
{
    return os << static_cast<void const*>( auto_ptr.get() );
}

//---------------------------------------------------------------------------//

}   // namespace sbe

#endif  //  #ifndef SBE_AUTO_PTR_HPP_INCLUDED  //
