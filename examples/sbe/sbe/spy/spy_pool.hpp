#ifndef SBE_SPY_POOL_HPP_INCLUDED
#define SBE_SPY_POOL_HPP_INCLUDED

#include "spy_ptr.hpp"
#include "spy_hash.hpp"
#include "spy_locker.hpp"
#include "spy_stat.hpp"

namespace sbe{
namespace spy{

//---------------------------------------------------------------------------//

class  UsedItem: public IntrusiveList<UsedItem>
{
protected:
    inline UsedItem( void )
        : IntrusiveList<UsedItem>()
        {}
    
    inline ~UsedItem( void )
    {}
}

class  PoolItem: protected UsedItem, HashItem
{
protected:
    inline PoolItem( void )
        : UsedItem()
        , HashItem()
    {}
    
    inline ~PoolItem( void )
    {}
};

//---------------------------------------------------------------------------//

template <class T, size_t  t_hash_size >
class Pool
{
    UsedItem*                   used_list_;
    UsedItem*                   free_list_;
    
    Hash< T, t_hash_size >      hash_;
    
    //=======================================================//
public:
    
    Pool( void )
        : used_list_( NULL )
        , free_list_( NULL )
        , hash_()
    {}
    
    //-------------------------------------------------------//
    
    inline  ~Pool( void )
    {}
    
    //-------------------------------------------------------//
    
    T*   popFreeItem( void )
    {
        return static_cast<T*>(listPopFront( &this->free_list_ ));
    }
    
    void    pushFreeItem( UsedItem*  item )
    {
        SBE_ASSERT( (item != NULL) && item->single() );
        
        listPushBack( &this->free_list_, item );
    }
    
    T*   popUsedItem( void )
    {
        
    }
    
    void    pushUsedItem( T*  item )
    {
        listPushBack( &this->used_list_, item );
        this->hash_.insertFront( item );
    }
    
    void    removeUsedItem( T*  item )
    {
        
    }
    
    
    
    
    Item*   allocate( void );
    void    insert( Item* item );
    void    free( Item* item );
    
    
        
        void    appendItem( PtrData const &  ptr_data, CorruptedPtr*  corrupted_ptr );
        bool    removeItem( void const *  ptr, PtrData*  ptr_data, CallTree const &  call_tree );
        
        void    reset( void );
        
        inline Stat*        stat( void )        { return &this->stat_; }    //lint !e1536   //Warning -- Exposing low access member
        inline Stat const*  stat( void ) const  { return &this->stat_; }
        
        static Pool*        instance( void );
    
    private:
        
        inline void     pushAllocatedItem( AllocatedList*  item );
        inline void     popAllocatedItem( AllocatedList*  item );
        inline PtrList* dropAllocatedItem( void );
        
        inline void     pushFreeItem( PtrList*  item );
        inline PtrList* popFreeItem( void );
        
        
        Pool( Pool const &   pool );                    // no copy
        Pool&   operator=( Pool const &   pool );       // no copy
};

//===========================================================================//

class AllocatedListFwdIterator
{
        Pool*               pool_;
        AllocatedList*      list_;
        
        AllocatedListFwdIterator( AllocatedListFwdIterator const & );                   // no copy
        AllocatedListFwdIterator&    operator=( AllocatedListFwdIterator const & );     // no copy
    
    public:
        explicit AllocatedListFwdIterator( Pool *  pool );
        AllocatedListFwdIterator( Pool *  pool, void const * ptr );
        
        ~AllocatedListFwdIterator( void );
        
        AllocatedListFwdIterator&   operator++( void );
        
        inline bool     valid( void ) const         { return this->list_ != NULL; }
        
        inline PtrData &     operator*( void )      { return *this->list_; }
        inline PtrData *     operator->( void )     { return this->list_; }
};

//===========================================================================//

class FreeListFwdIterator
{
        Pool*               pool_;
        PtrList const *     list_;
        
        FreeListFwdIterator( FreeListFwdIterator const & );                 // no copy
        FreeListFwdIterator&    operator=( FreeListFwdIterator const & );   // no copy
    
    public:
        explicit FreeListFwdIterator( Pool *  pool );
        ~FreeListFwdIterator( void );
        
        FreeListFwdIterator&   operator++( void );
        
        inline bool     valid( void ) const      { return this->list_ != NULL; }
        
        inline PtrData const &     operator*( void ) const      { return *this->list_; }
        inline PtrData const *     operator->( void ) const     { return this->list_; }
};


}   // namespace spy
}   // namespace sbe

#endif  // #ifndef SBE_SPY_POOL_HPP_INCLUDED

