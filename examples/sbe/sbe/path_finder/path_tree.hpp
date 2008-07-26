#ifndef PATH_TREE_HPP_INCLUDED
#define PATH_TREE_HPP_INCLUDED

#include <stddef.h>
#include <cstdio>
#include <memory>
#include <cstring>

namespace sbe{

/*
    Flexelint workaround, it doesn't understand template friends yet
*/
#ifdef _lint
    #define LINT_PUBLIC     public:
    #define LINT_PRIVATE    private:
#else
    #define LINT_PUBLIC
    #define LINT_PRIVATE
#endif

//===========================================================================//

template <class TNode>
struct   PathTreeNodeIterator
{
private:
    template <typename T, size_t  t_directions, class TAllocator>   friend class PathTree;
    
    typedef PathTreeNodeIterator<TNode>     ThisType;
    typedef TNode                           Node;

public:
    typedef typename Node::value_type       value_type;
    typedef typename Node::pointer          pointer;
    typedef typename Node::reference        reference;
    
private:
LINT_PUBLIC
    Node*       node_;
    
    #ifdef SBE_DEBUG
        ThisType*   next_;
    #endif
    
    inline void     linkNode( void )
    #ifndef SBE_DEBUG
    const
    #endif
    {
        #ifdef SBE_DEBUG
        if (this->node_ != NULL)
        {
            this->next_ = this->node_->it_;
            this->node_->it_ = this;
        }
        #endif
    }
    
    //-------------------------------------------------------//
    
    inline void     unlinkNode( void )
    #ifndef SBE_DEBUG
    const
    #endif
    {
        #ifdef SBE_DEBUG
        if (this->node_ != NULL)
        {
            ThisType**   node_it = &this->node_->it_;
            
            for (; *node_it != this; node_it = &((*node_it)->next_) )
            {}
            
            *node_it = this->next_;
        }
        #endif
    }
    
LINT_PRIVATE
public:
    inline ~PathTreeNodeIterator( void )                                    { this->unlinkNode(); }
    
    inline PathTreeNodeIterator( void )
        : node_( NULL )
        #if defined(SBE_DEBUG) && defined(_lint)
        , next_( NULL )
        #endif
    {}
    
    inline explicit PathTreeNodeIterator( Node*  node ) : node_( node )     { this->linkNode(); }
    
    inline PathTreeNodeIterator( ThisType const &  it ) : node_( it.node_ ) { this->linkNode(); }
    
    inline ThisType&    operator=( ThisType const &  it )       //lint --e{1529}    // Warning -- Symbol not first checking for assignment to this
    {
        this->unlinkNode();
        
        this->node_ = it.node_;     //lint !e1555   //Warning -- Direct pointer copy of member
        
        this->linkNode();
        
        return *this;
    }
    
    //-------------------------------------------------------//
    
    inline ThisType&    operator++( void )
    {
        Node*   node = this->node_;
        if (node != NULL)
        {
            this->unlinkNode();
            
            this->node_ = node->parent_;
            
            this->linkNode();
        }
        
        return *this;
    }
    
    //-------------------------------------------------------//
    
    inline ThisType     operator++(int)
    {
        ThisType    tmp( *this );
        
        ++*this;
        
        return tmp;
    }
    
    //-------------------------------------------------------//
    
    inline reference            operator*( void )           { SBE_ASSERT( this->node_ != NULL ); return this->node_->obj_; }
    inline value_type const&    operator*( void )  const    { SBE_ASSERT( this->node_ != NULL ); return this->node_->obj_; }
    
    inline pointer              operator->( void )          { SBE_ASSERT( this->node_ != NULL ); return &this->node_->obj_; }
    inline value_type const*    operator->( void )  const   { SBE_ASSERT( this->node_ != NULL ); return &this->node_->obj_; }
    
    friend inline bool         operator==(ThisType const & it1, ThisType const & it2)       { return it1.node_ == it2.node_; }
    friend inline bool         operator!=(ThisType const & it1, ThisType const & it2)       { return it1.node_ != it2.node_; }
    
    #ifdef SBE_DEBUG
        inline bool     isLast( void ) const    { SBE_ASSERT( this->node_ != NULL );    return this->node_->isLast(); }
        inline size_t   size( void ) const      { SBE_ASSERT( this->node_ != NULL );    return this->node_->size(); }
        inline void     print( void ) const     { SBE_ASSERT( this->node_ != NULL );    this->node_->print(); }
    #endif  // #ifdef SBE_DEBUG
};

//===========================================================================//

template <typename T, size_t  t_directions>
struct  PathTreeNode
{
private:
LINT_PUBLIC
    template <class U, size_t  u_directions, class TAllocator>  friend class PathTree;
    template <class TNode>                                      friend struct PathTreeNodeIterator;
    
    typedef PathTreeNode<T, t_directions>   ThisType;
    
    typedef T       value_type;
    typedef T*      pointer;
    typedef T&      reference;
    
    ThisType*       parent_;
    ThisType*       child_[ t_directions ];
    
    T               obj_;
    
    #ifdef SBE_DEBUG
        PathTreeNodeIterator<ThisType>*         it_;            // pointer to iterators list, it's used to invalidate iterators
    #endif
    
    PathTreeNode( ThisType const &  node );             // no copy
    ThisType&   operator=( ThisType const &  node );    // no copy
    
    PathTreeNode( void );           // default constructor is never called
    ~PathTreeNode( void );          // destructor is never called either
    
    //-------------------------------------------------------//
    
    inline void    init( void )
    {
        this->parent_ = NULL;
        
        for (size_t  i = 0; i < t_directions; ++i)
        {
            this->child_[i] = NULL;
        }
    }
    
    //-------------------------------------------------------//
    
    inline void    link( ThisType*  child, size_t  direction)
    {
        SBE_ASSERT( direction < t_directions );
        SBE_ASSERT( this->test() );
        SBE_ASSERT( this->child_[direction] == NULL );
        
        this->child_[ direction ] = child;
        
        child->parent_ = this;
        
        for (size_t  i = 0; i < t_directions; ++i)
        {
            child->child_[i] = NULL;
        }
    }
    
    //-------------------------------------------------------//
    
    bool    unlinkLast( ThisType const *  child )
    {
        bool    is_last = true;
        
        for (size_t  i = 0; i < t_directions; ++i)
        {
            ThisType const* const   c = this->child_[i];
            
            if (c != NULL)
            {
                if (c == child)
                {
                    this->child_[i] = NULL;
                }
                else
                {
                    is_last = false;
                }
            }
        }
        
        return is_last;
    }
    
    //-------------------------------------------------------//

#ifdef SBE_DEBUG
LINT_PRIVATE
public:
    
    inline bool     isLast( void ) const
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
    
    //-------------------------------------------------------//
    
    inline size_t   size( void ) const
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
    
    //-------------------------------------------------------//
    
    bool    test( void ) const
    {
        ThisType const* const   p = this->parent_;
        
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
            if (this->child_[i] != NULL)
            {
                if (this->child_[i]->parent_ != this)
                {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    //-------------------------------------------------------//
    
    void    print( size_t  depth = 0 ) const
    {
    SBE_ASSERT( this->test() );
        
        char    prefix[256];
        
        std::memset( prefix, ' ', depth * 4 );
        prefix[ depth * 4 ] = '\0';
        
        std::printf( "%s%p) parent: %p\n", prefix, this, const_cast<ThisType const*>(this->parent_) );
        
        for (size_t  i = 0; i < t_directions; ++i)
        {
            std::printf( "%s%u) child: %p\n", prefix, i, const_cast<ThisType const*>( this->child_[i] ) );
            
            if (this->child_[i] != NULL)
            {
                this->child_[i]->print( depth + 1 );
            }
        }
    }
#endif  // #ifdef SBE_DEBUG
};

//===========================================================================//

template <typename T, class TAllocator>
class AllocatorGuardian
{
    T*              ptr_;
    TAllocator*     allocator_;
    
    typedef AllocatorGuardian< T, TAllocator>      ThisType;
    
    AllocatorGuardian( ThisType const &  guard );           // no copy
    ThisType&   operator=( ThisType const &  guard );       // no copy
    
public:
    inline AllocatorGuardian( T*  ptr, TAllocator*  allocator )
        : ptr_(ptr)
        , allocator_( allocator )
    {
        SBE_ASSERT( ptr != NULL );
        SBE_ASSERT( allocator != NULL );
    }
    
    //-------------------------------------------------------//
    
    inline ~AllocatorGuardian( void )
    {   
        if (this->ptr_ != NULL)
        {
            this->allocator_->deallocate( this->ptr_, 1 );
        }
    }
    
    //-------------------------------------------------------//
    
    inline void     release(void)
    {
        this->ptr_ = NULL;
    }
};

//===========================================================================//

template <typename T, size_t  t_directions = 4, class TAllocator = std::allocator<T> >
class   PathTree
{
    typedef PathTree<T, t_directions, TAllocator>               ThisType;
    typedef PathTreeNode<T, t_directions>                       Node;
    typedef typename TAllocator::template rebind<Node>::other   NodeAllocator;

public:
    typedef T                                               value_type;
    typedef typename TAllocator::pointer                    pointer;
    typedef typename TAllocator::const_pointer              const_pointer;
    typedef typename TAllocator::reference                  reference;
    typedef typename TAllocator::const_reference            const_reference;
    typedef PathTreeNodeIterator< Node >                    iterator;
    typedef size_t                                          size_type;
    typedef ptrdiff_t                                       difference_type;
    typedef TAllocator                                      allocator_type;
    
private:
    Node*           node_;
    NodeAllocator   node_allocator_;
    TAllocator      obj_allocator_;
    
    #ifdef SBE_DEBUG
        size_t      size_;
    #endif
    
    
public:
    PathTree( ThisType const &  path );
    ThisType&   operator=( ThisType const &  path );
    
    //-------------------------------------------------------//
    
    inline PathTree( void )
        : node_( NULL )
        , node_allocator_()
        , obj_allocator_()
        #ifdef SBE_DEBUG
        , size_( 0 )
        #endif
    
    {}
    
    //-------------------------------------------------------//
    
    inline ~PathTree( void )
    {
        this->destroy( this->node_ );
    }
    
    //-------------------------------------------------------//
    
    inline iterator         end( void )         { return iterator(); }
    
    //-------------------------------------------------------//
    
    iterator    attach( T const &  obj )
    {
        SBE_ASSERT( this->test() );
        SBE_ASSERT( this->node_ == NULL );
        
        Node* const     node = this->createNode( obj );
        
        node->init();
        this->node_ = node;
        
        return iterator( node );
    }
    
    //-------------------------------------------------------//
    
    iterator   attach( T const &  obj, iterator const &  parent, size_t  direction )
    {
        SBE_ASSERT( this->test() );
        SBE_ASSERT( this->node_ != NULL );
        SBE_ASSERT( parent != end() );
        
        Node* const     node = this->createNode( obj );
        
        parent.node_->link( node, direction );
        
        return iterator( node );
    }
    
    //-------------------------------------------------------//
    
    void    collapse( iterator const &  pos )
    {
        Node*   node = pos.node_;
    
    SBE_ASSERT( this->test() );
    SBE_ASSERT( this->node_ != NULL );
    SBE_ASSERT( node != NULL );
    SBE_ASSERT( node->test() );
    SBE_ASSERT( node->isLast() );
        
        for(;;)
        {
            Node* const     p = node->parent_;
            
            bool            stop;
            
            if (p != NULL)
            {
                stop = !p->unlinkLast( node );      // stop collapsing if it's not the last node
            }
            else
            {
                stop = true;
                this->node_ = NULL;
            }
            
            this->destroyNode( node );
            
            if (stop)
            {
                return;
            }
            
            node = p;
        }
    }
    
    //-------------------------------------------------------//
    
    #ifdef SBE_DEBUG
        inline size_t   size( void ) const
        {
        SBE_ASSERT( this->test() );
        SBE_ASSERT( (this->node_ == NULL) || (this->size_ == this->node_->size()) );
        
            return this->size_;
        }
    #endif  // #ifdef SBE_DEBUG
    
    //-------------------------------------------------------//
private:
    
    void    destroy( Node*  node )
    {
        if (node != NULL)
        {
            SBE_ASSERT( node->test() );
            
            for (size_t  i = 0; i < t_directions; ++i)
            {
                this->destroy( node->child_[i] );
            }
            
            this->destroyNode( node );
        }
    }
    
    //-------------------------------------------------------//
    
    Node*   createNode( T const &  obj )
    {
        Node* const     node = this->node_allocator_.allocate( 1 );
        
        AllocatorGuardian< Node, NodeAllocator >   node_guardian( node, &this->node_allocator_ );
        
        this->obj_allocator_.construct( &node->obj_, obj );
        
        node_guardian.release();
        
        #ifdef SBE_DEBUG
            ++this->size_;
            node->it_ = NULL;
        #endif
        
        return node;
    }
    
    //-------------------------------------------------------//
    
    void    destroyNode( Node*  node )
    {
        SBE_ASSERT( this->size_ > 0 );
        
        #ifdef SBE_DEBUG
            --this->size_;
            
            // invalidate all iterators, which are referencing to this node
            for (iterator*  it = node->it_; it != NULL; it = it->next_ )
            {
                it->node_ = NULL;
            }
        #endif
        
        this->obj_allocator_.destroy( &node->obj_ );
        this->node_allocator_.deallocate( node, 1 );
    }
    
    //-------------------------------------------------------//
    
    #ifdef SBE_DEBUG
        bool    test( void )    const
        {
            return ((this->node_ == NULL) && (this->size_ == 0)) ||
                   ((this->node_ != NULL) && (this->size_ > 0));
        }
    #endif  // #ifdef SBE_DEBUG
    
    //-------------------------------------------------------//
    
    #ifdef SBE_DEBUG
public:
    void    print( void ) const
    {
        SBE_ASSERT( this->test() );
        
        if (this->node_ != NULL)
        {
            this->node_->print();
        }
    }
    #endif  // #ifdef SBE_DEBUG
};

//===========================================================================//

}   // namespace sbe

#endif  // #ifndef PATH_TREE_HPP_INCLUDED
