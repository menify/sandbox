#ifndef MULTI_PATH_HPP_INCLUDED
#define MULTI_PATH_HPP_INCLUDED

#include <stddef.h>
#include <memory>

namespace sbe{

template <class T, size_t  t_directions = 4, template <class> class TAllocator = std::allocator>
class   IntrusivePathTree
{
    typedef IntrusivePathTree<T, t_directions, TAllocator>      ThisType;
    
    T*          parent_;
    T*          child_[ t_directions ];
    
    
    IntrusivePathTree( ThisType const &  wp );          // no copy
    ThisType&   operator=( ThisType const &  wp );      // no copy
    
                                                        // forbid unsupported allocation operators
    static void*    operator new[]( size_t  size );
    static void     operator delete[]( void*  ptr );
    
    static void*    operator new(size_t, const std::nothrow_t&);
    static void     operator delete(void*, const std::nothrow_t&);
    static void*    operator new[](size_t, const std::nothrow_t&);
    static void     operator delete[](void*, const std::nothrow_t&);
    
    static void*    operator new(size_t, void*);
    static void*    operator new[](size_t, void*);
    static void     operator delete  (void*, void*) throw();
    static void     operator delete[](void*, void*) throw();
    
protected:
    inline IntrusivePathTree( void );
    ~IntrusivePathTree( void );

public:
    static inline void*     operator new( size_t  size );       // specialized allocation operators
    static inline void      operator delete( void*  ptr );
    
    inline T*           parent( void )                  { return static_cast<T*>(this->parent_); }
    inline T const *    parent( void ) const            { return static_cast<T const*>(this->parent_); }
    inline bool         isRoot( void ) const            { return this->parent_ == NULL; }
    inline bool         isLast( void ) const;
    
    inline T*           attach( size_t  direction )     { return this->attach( direction, new T ); }
    inline T*           attach( size_t  direction, T*  child );
    void                collapse( void );
    
    bool                test( void );
};

//---------------------------------------------------------------------------//

template <class T, size_t  t_directions, template <class> class TAllocator>
inline void*    IntrusivePathTree<T, t_directions, TAllocator>::operator new( size_t )
{
    return TAllocator<T>().allocate( 1 );
}

template <class T, size_t  t_directions, template <class> class TAllocator>
inline void     IntrusivePathTree<T, t_directions, TAllocator>::operator delete( void *  ptr )
{
    return TAllocator<T>().deallocate( static_cast<T*>(ptr), 1 );
}

//---------------------------------------------------------------------------//

template <class T, size_t  t_directions, template <class> class TAllocator>
inline IntrusivePathTree<T, t_directions, TAllocator>::IntrusivePathTree( void )
:   parent_( NULL )
{
    for (size_t  i = 0; i < t_directions; ++i)
    {
        this->child_[i] = NULL;
    }
}

//---------------------------------------------------------------------------//

template <class T, size_t  t_directions, template <class> class TAllocator>
IntrusivePathTree<T, t_directions, TAllocator>::~IntrusivePathTree( void )
{
SBE_ASSERT( this->test() );
    
    T*  p = this->parent_;
    
    if (p != NULL)
    {
        for (size_t  i = 0; i < t_directions; ++i)
        {
            if (p->child_[i] == this)
            {
                p->child_[i] = NULL;
                break;
            }
        }
    }
    
    //-------------------------------------------------------//
    
    for (size_t  i = 0; i < t_directions; ++i)
    {
        T*  child = this->child_[i];
        
        if (child != NULL)
        {
            child->parent_ = NULL;                  // break off the relation with the parent node
            delete child;
        }
    }
}

//---------------------------------------------------------------------------//

template <class T, size_t  t_directions, template <class> class TAllocator>
inline bool    IntrusivePathTree<T, t_directions, TAllocator>::isLast( void ) const
{
    for (size_t  i = 0; i < t_directions; ++i)
    {
        if (this->child_[i] != NULL)
        {
            return false;
        }
    }
    
    return true;
}

//---------------------------------------------------------------------------//

template <class T, size_t  t_directions, template <class> class TAllocator>
void    IntrusivePathTree<T, t_directions, TAllocator>::collapse( void )
{
SBE_ASSERT( this->test() );
SBE_ASSERT( this->isLast() );
    
    T*   p;
    T*   child = static_cast<T*>(this);
    
    for (;;)
    {
        p = child->parent_;
        
        if (p == NULL)
        {
            break;
        }
        
        delete child;
        
        if (!p->isLast())
        {
            break;
        }
        
        child = p;
    }
}

//---------------------------------------------------------------------------//

template <class T, size_t  t_directions, template <class> class TAllocator>
inline T*   IntrusivePathTree<T, t_directions, TAllocator>::attach(
    
    size_t      direction,
    T*          child
)
{
SBE_ASSERT( direction < t_directions );
SBE_ASSERT( this->child_[direction] == NULL );
SBE_ASSERT( child != NULL );
SBE_ASSERT( child->isRoot() && child->isLast() );
    
    this->child_[ direction ] = child;
    child->parent_ = static_cast<T*>(this);
    
    return child;
}

//---------------------------------------------------------------------------//

template <class T, size_t  t_directions, template <class> class TAllocator>
bool    IntrusivePathTree<T, t_directions, TAllocator>::test( void )
{
    T*  p = this->parent_;
    
    if (p != NULL)
    {
        size_t  i;
        
        for (i = 0; i < t_directions; ++i)
        {
            if (p->child_[i] == this)
            {
                break;
            }
        }
        
        if (i == t_directions)
        {
            return false;
        }
    }
    
    //-------------------------------------------------------//
    
    for (size_t  i = 0; i < t_directions; ++i)
    {
        T*   child = this->child_[i];
        
        if (child != NULL)
        {
            if (child->parent_ != this)
            {
                return false;
            }
        }
    }
    
    return true;
}

//---------------------------------------------------------------------------//

}   // namespace sbe

#endif  // #ifndef MULTI_PATH_HPP_INCLUDED
