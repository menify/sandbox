#ifndef SBE_TYPE_EXPLORER_HPP_INCLUDED
#define SBE_TYPE_EXPLORER_HPP_INCLUDED

namespace sbe{

template <typename T, typename U>
class   ConversionChecker
{
    typedef char    Possible;
    class Impossible { Possible[2]; }
    
    Possible        check(U);
    Impossible      check(...);
    T               makeT();
    
public:
    enum    { possible = (sizeof(check( makeT() ) ) == sizeof(Possible)) };
}



class   IntrusivePtrCounter
{
protected:
    
    size_t      ptr_references_;
    
public:
    
    inline IntrusivePtrCounter( void )      : ptr_references_(0) {}
    inline ~IntrusivePtrCounter( void ){}
};

class   Foo:    public IntrusivePtrCounter
{
    size_t      count;
};

SafePtr< Foo >      foo;

ConversionChecker< Foo, IntrusivePtrCounter>::possible

SafePtr: public ReferenceCounter< ConversionChecker< T, IntrusivePtrCounter>::possible >


template <typename T, bool intrusive>
class ReferenceCounter
{
    typedef ReferenceCounter<T,intrusive>   ThisType;
public:
    
    inline ReferenceCounter( void )
    
    inline void     init( T*  ptr )         { this->next_ = this; this->prev_ = this; }
    inline bool     single( void ) const    { return this->next_ == this; }
    
    inline void     link( ThisType*  ref );
    inline void     unlink( void );
    
    bool            test( void ) const;
}

template <typename T>
class Reference<T, false>
{
    typedef ReferenceCounter<T,intrusive>   ThisType;
    
    ThisType*       next_;
    ThisType*       prev_;
    
public:
    inline void     init( T*  ptr )         { this->next_ = this; this->prev_ = this; }
    inline bool     single( void ) const    { return this->next_ == this; }
    
    inline void     link( ThisType*  ref );
    inline void     unlink( void );
    
    bool            test( void ) const;
};



}   // namespace sbe

#endif  // #ifndef SBE_TYPE_EXPLORER_HPP_INCLUDED
