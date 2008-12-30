#ifndef SBE_SPY_POOL_HPP_INCLUDED
#define SBE_SPY_POOL_HPP_INCLUDED

#include "spy_ptr.hpp"
#include "spy_hash.hpp"
#include "spy_locker.hpp"
#include "spy_stat.hpp"

namespace sbe{
namespace spy{

//---------------------------------------------------------------------------//

class  UsedItem: public ListItem<UsedItem>
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
    typedef List<HashItem>      UsedList;
    
    UsedList                    used_list_;
    UsedList                    free_list_;
    
    Hash< T, t_hash_size >      hash_;
    
    //=======================================================//
public:
    
    Pool( void )
        : used_list_()
        , free_list_()
        , hash_()
    {}
    
    //-------------------------------------------------------//
    
    inline  ~Pool( void )
    {}
    
    //-------------------------------------------------------//
    
    inline T*       popFreeItem( void )
    {
        return static_cast<T*>(this->free_list_.popFront());
    }
    
    //-------------------------------------------------------//
    
    inline void     pushFreeItem( UsedItem*  item )
    {
        this->free_list_.pushBack( item );
    }
    
    //-------------------------------------------------------//
    
    void    pushUsedItem( T*  item )
    {
        this->used_list_.pushBack( item );
        this->hash_.insert( item );
    }
    
    //-------------------------------------------------------//
    
    inline void     popUsedItem( T*  item )
    {
        this->used_list_.pop( item );
        this->hash_.remove( item );
    }
    
    //-------------------------------------------------------//
    
    inline T*   popUsedItem( void )
    {
        T*  item = static_cast<T*>(this->used_list_.popFront());
        this->hash_.remove( item );
        
        return item;
    }
    
    //-------------------------------------------------------//
    
    private:
        Pool( Pool const &   pool );                    // no copy
        Pool&   operator=( Pool const &   pool );       // no copy
};

}   // namespace spy
}   // namespace sbe

#endif  // #ifndef SBE_SPY_POOL_HPP_INCLUDED

