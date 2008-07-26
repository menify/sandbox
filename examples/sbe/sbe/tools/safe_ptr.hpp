#ifndef SBE_MANAGED_PTR_HPP_INCLUDED
#define SBE_MANAGED_PTR_HPP_INCLUDED

#include "sbe/ut/debug.hpp"
#include "sbe/tools/deleters.hpp"

namespace sbe{

//---------------------------------------------------------------------------//

/*
    Class: SafePtr
    This is smart pointer class. It uses linked list to track longevity of a object.
    Creation of this class is absolutely safe operation, because it doesn't use a dynamic memory 
    for its internal data (unlike of counter based smart pointers).
    By default it uses operator 'delete' to delete a object.
    But it's possible to override a delete strategy (like <NewArrayDeleter>).
    
    Parameters:
        T           - a type which is being pointed to
        TDeleter    - a functor, which is used to destroy an object
    
    See also:
        <Deleters>
*/
template <typename T, class TDeleter = NewDeleter<T> >
class SafePtr
{
public:
    typedef T   element_type;
    
private:
    typedef SafePtr<T, TDeleter>        ThisType;
    
    T*          ptr_;
    
    ThisType*   next_;
    ThisType*   prev_;
    
    inline void     init( T*  ptr )         { this->ptr_ = ptr; this->next_ = this; this->prev_ = this; }
    inline bool     single( void ) const    { return this->next_ == this; }
    
    inline void     link( ThisType*  safe_ptr );
    inline void     unlink( void );
    
    bool            linked( ThisType const *  safe_ptr ) const;
    bool            test( void ) const;
        
public:
    
    inline SafePtr( void )                          { this->init( NULL ); }
    explicit inline SafePtr( T*  p )                { this->init( p ); }
    inline SafePtr( ThisType const &  safe_ptr )    { const_cast<ThisType*>(&safe_ptr)->link( this ); }
    inline ~SafePtr( void )                         { this->unlink(); }
    
    
    inline ThisType&    operator=( ThisType const &  safe_ptr )     { this->reset( safe_ptr ); return *this; }
    inline ThisType&    operator=( T*  ptr )                        { this->reset( ptr ); return *this; }
    
    inline T*           get( void )                                 { return this->ptr_; }
    inline T const*     get( void ) const                           { return this->ptr_; }
    
    inline void         reset( T*  ptr = NULL )                     { if (ptr != this->ptr_) { this->unlink(); this->init( ptr ); } }
    inline void         reset( ThisType const &  safe_ptr )         { SBE_ASSERT( (safe_ptr.ptr_ != this->ptr_) || this->linked( &safe_ptr ) );
                                                                      this->unlink(); const_cast<ThisType*>(&safe_ptr)->link( this ); }
    
    inline T&           operator*( void )                           { SBE_ASSERT( this->ptr_ != NULL ); return *this->ptr_; }
    inline T const&     operator*( void ) const                     { SBE_ASSERT( this->ptr_ != NULL ); return *this->ptr_; }
    
    inline T*           operator->( void )                          { SBE_ASSERT( this->ptr_ != NULL ); return this->ptr_; }
    inline T const*     operator->( void ) const                    { SBE_ASSERT( this->ptr_ != NULL ); return this->ptr_; }
    
    inline T&           operator []( unsigned long   index )        { SBE_ASSERT(this->ptr_ != NULL); return this->ptr_[ index ]; }
    inline T const&     operator []( unsigned long   index ) const  { SBE_ASSERT(this->ptr_ != NULL); return this->ptr_[ index ]; }
    
    inline bool         operator !( void )   const                              { return this->ptr_ == NULL; }
    
    inline friend bool  operator ==( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ == p2.ptr_; }
    inline friend bool  operator ==( ThisType const&  p1, T const*  p2)         { return p1.ptr_ == p2; }
    inline friend bool  operator ==( T const*  p2, ThisType const&  p1)         { return p1.ptr_ == p2; }
    
    inline friend bool  operator !=( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ != p2.ptr_; }
    inline friend bool  operator !=( ThisType const&  p1, T const*  p2)         { return p1.ptr_ != p2; }
    inline friend bool  operator !=( T const*  p2, ThisType const&  p1)         { return p1.ptr_ != p2; }
    
    inline friend bool  operator <( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ < p2.ptr_; }
    inline friend bool  operator <( ThisType const&  p1, T const*  p2)         { return p1.ptr_ < p2; }
    inline friend bool  operator <( T const*  p2, ThisType const&  p1)         { return p2 < p1.ptr_; }
    
    inline friend bool  operator <=( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ <= p2.ptr_; }
    inline friend bool  operator <=( ThisType const&  p1, T const*  p2)         { return p1.ptr_ <= p2; }
    inline friend bool  operator <=( T const*  p2, ThisType const&  p1)         { return p2 <= p1.ptr_; }
    
    inline friend bool  operator >( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ > p2.ptr_; }
    inline friend bool  operator >( ThisType const&  p1, T const*  p2)         { return p1.ptr_ > p2; }
    inline friend bool  operator >( T const*  p2, ThisType const&  p1)         { return p2 > p1.ptr_; }
    
    inline friend bool  operator >=( ThisType const&  p1, ThisType const&  p2)  { return p1.ptr_ >= p2.ptr_; }
    inline friend bool  operator >=( ThisType const&  p1, T const*  p2)         { return p1.ptr_ >= p2; }
    inline friend bool  operator >=( T const*  p2, ThisType const&  p1)         { return p2 >= p1.ptr_; }
};

//---------------------------------------------------------------------------//

template <typename T, class TDeleter>
inline void     SafePtr<T,TDeleter>::link( ThisType*  safe_ptr )
{
SBE_ASSERT( this->test() );
    
    safe_ptr->ptr_ = this->ptr_;
    
    ThisType*       next = this->next_;
    
    safe_ptr->next_ = next;
    safe_ptr->prev_ = this;
    
    this->next_ = safe_ptr;
    next->prev_ = safe_ptr;
}

//---------------------------------------------------------------------------//

template <typename T, class TDeleter>
inline void     SafePtr<T,TDeleter>::unlink( void )
{
SBE_ASSERT( this->test() );
    
    if (this->single())
    {
        TDeleter()( this->ptr_ );
        return;
    }
    
    ThisType*     prev;
    ThisType*     next;
    
    next = this->next_;
    prev = this->prev_;
    
    prev->next_ = next;
    next->prev_ = prev;
}

//---------------------------------------------------------------------------//

template <typename T, class TDeleter>
bool     SafePtr<T,TDeleter>::linked( ThisType const*  safe_ptr ) const
{
SBE_ASSERT( this->test() );

    ThisType const *    current = this;
    
    do
    {
        if (current == safe_ptr)
        {
            return true;
        }
        
        current = current->next_;
    }
    while (current != this);
    
    return false;
}

//---------------------------------------------------------------------------//

template <typename T, class TDeleter>
bool     SafePtr<T,TDeleter>::test( void ) const
{
    ThisType const *    next;
    ThisType const *    prev;
    
    prev = this;
    
    do
    {
        next = prev->next_;
        
        if (next->prev_ != prev )
        {
            return false;
        }
        
        prev = next;
    }
    while (next != this);
    
    return true;
}

//---------------------------------------------------------------------------//

template<typename T, class TDeleter, typename CharT, typename Traits >
inline std::basic_ostream< CharT, Traits>& operator<< (
    
    std::basic_ostream<CharT, Traits>&      os,
    SafePtr<T,TDeleter> const &             safe_ptr
)
{
    return os << static_cast<void const*>( safe_ptr.get() );
}

//---------------------------------------------------------------------------//

}   // namespace sbe

#endif  //  #ifndef SBE_MANAGED_PTR_HPP_INCLUDED  //
