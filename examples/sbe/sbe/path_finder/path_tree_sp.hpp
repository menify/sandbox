#ifndef PATH_TREE_HPP_INCLUDED
#define PATH_TREE_HPP_INCLUDED

#include <stddef.h>

namespace sbe{

template <class TSmartPointer, size_t  t_directions = 4 >
class   IntrusivePathTree
{
    typedef IntrusivePathTree<TSmartPointer, t_directions>      ThisType;
    typedef typename TSmartPointer::element_type                Node;
    
    Node*           parent_;
    TSmartPointer   child_[ t_directions ];
    
    IntrusivePathTree( ThisType const &  wp );          // no copy
    ThisType&   operator=( ThisType const &  wp );      // no copy
    
protected:
    inline IntrusivePathTree( void )    : parent_( NULL )   {}
    inline ~IntrusivePathTree( void )                       {}

public:
    inline Node*            parent( void )          { return this->parent_; }
    inline Node const*      parent( void ) const    { return this->parent_; }
    
    inline bool             isRoot( void ) const    { return this->parent_ == NULL; }
    inline bool             isLast( void ) const;
    
    inline size_t           size( void ) const;
    void                    print( size_t  depth = 0 ) const;
    
    void                    attach( size_t  direction, TSmartPointer&  child );
    void                    collapse( void );
    
    bool                    test( void ) const;
};

//---------------------------------------------------------------------------//

template <class TSmartPointer, size_t  t_directions>
inline void     IntrusivePathTree<TSmartPointer, t_directions>::attach(
    
    size_t              direction,
    TSmartPointer&      child
)
{
SBE_ASSERT( direction < t_directions );
SBE_ASSERT( this->child_[direction] == NULL );
SBE_ASSERT( child != NULL );
SBE_ASSERT( child->isRoot() && child->isLast() );
    
    this->child_[ direction ] = child;
    child->parent_ = static_cast<Node*>(this);
}

//---------------------------------------------------------------------------//

template <class TSmartPointer, size_t  t_directions>
inline void     IntrusivePathTree<TSmartPointer, t_directions>::collapse( void )
{
SBE_ASSERT( this->test() );
SBE_ASSERT( this->isLast() );
    
    Node*       node = static_cast<Node*>(this);
    bool        stop = false;
    
    for(;;)
    {
        Node*   p = node->parent_;
        
        if (p == NULL)
        {
            return;
        }
        
        for (size_t  i = 0; i < t_directions; ++i)
        {
            if (p->child_[i] != NULL)
            {
                if (p->child_[i].get() == node)
                {
                    p->child_[i]->parent_ = NULL;
                    p->child_[i].reset();
                }
                else
                {
                    // there is at least one another child, we can't keep collapsing anymore
                    stop = true;
                }
            }
        }
        
        if (stop)
        {
            return;
        }
        
        node = p;
    }
}

//---------------------------------------------------------------------------//

template <class TSmartPointer, size_t  t_directions>
inline bool    IntrusivePathTree<TSmartPointer, t_directions>::isLast( void ) const
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

template <class TSmartPointer, size_t  t_directions>
inline size_t   IntrusivePathTree<TSmartPointer, t_directions>::size( void ) const
{
SBE_ASSERT( this->test() );
    
    size_t      n = 1;
    
    for (size_t  i = 0; i < t_directions; ++i)
    {
        if (this->child_[i] != NULL)
        {
            n += this->child_[i]->size();
        }
    }
    
    return n;
}

//---------------------------------------------------------------------------//

template <class TSmartPointer, size_t  t_directions>
inline void   IntrusivePathTree<TSmartPointer, t_directions>::print( size_t  depth ) const
{
SBE_ASSERT( this->test() );
    
    char    prefix[256];
    
    std::memset( prefix, ' ', depth * 4 );
    prefix[ depth * 4 ] = '\0';
    
    std::printf( "%s%p) parent: %p\n", prefix, this, this->parent_ );
    
    size_t      n = 1;
    
    for (size_t  i = 0; i < t_directions; ++i)
    {
        std::printf( "%s%u) child: %p\n", prefix, i, this->child_[i].get() );
        
        if (this->child_[i] != NULL)
        {
            this->child_[i]->print( depth + 1 );
        }
    }
}

//---------------------------------------------------------------------------//

template <class TSmartPointer, size_t  t_directions>
bool    IntrusivePathTree<TSmartPointer, t_directions>::test( void ) const
{
    Node const*     p = this->parent_;
    
    if (p != NULL)
    {
        size_t  i;
        
        for (i = 0; i < t_directions; ++i)
        {
            if (p->child_[i].get() == static_cast<Node const*>(this))
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
        if (this->child_[i] != NULL)
        {
            if (this->child_[i]->parent_ != static_cast<Node const*>(this))
            {
                return false;
            }
        }
    }
    
    return true;
}

//---------------------------------------------------------------------------//

}   // namespace sbe

#endif  // #ifndef PATH_TREE_HPP_INCLUDED
