#ifndef SBE_SPY_POOL_HPP_INCLUDED
#define SBE_SPY_POOL_HPP_INCLUDED

#include "spy_ptr.hpp"
#include "spy_hash.hpp"
#include "spy_locker.hpp"
#include "spy_stat.hpp"

namespace sbe{
namespace spy{

//---------------------------------------------------------------------------//

class  UsedItem: public ListItem
{
protected:
    inline UsedItem( void )
        : ListItem()
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
    typedef List<UsedItem>      UsedList;
    typedef Pool<T,t_hash_size> ThisType;
    
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
    
    inline T*       removeFreed( T*  item )
    {
        this->free_list_.pop( item );
    }
    
    //-------------------------------------------------------//
    
    inline void     addFreed( T*  item )
    {
        this->free_list_.pushBack( item );
    }
    
    //-------------------------------------------------------//
    
    inline T*   oldestFreed( void )
    {
        return this->free_list_.front();
    }
    
    //-------------------------------------------------------//
    
    inline T*   oldestUsed( void )
    {
        return this->used_list_.front();
    }
    
    //-------------------------------------------------------//
    
    inline void     addUsed( T*  item )
    {
        this->used_list_.pushBack( item );
        this->hash_.insert( item );
    }
    
    //-------------------------------------------------------//
    
    inline void     removeUsed( T*  item )
    {
        this->used_list_.pop( item );
        this->hash_.remove( item );
    }
    
    //-------------------------------------------------------//
    
    inline T const*   findUsed( T const&  item ) const
    {
        return this->hash_.get( item );
    }
    
    //-------------------------------------------------------//
    
    inline T*   findUsed( T const&  item )
    {
        return const_cast<T*>( const_cast<ThisType const*>(this)->findUsed( item ) );
    }
    
    private:
        Pool( Pool const &   pool );                    // no copy
        Pool&   operator=( Pool const &   pool );       // no copy
};

}   // namespace spy
}   // namespace sbe

#endif  // #ifndef SBE_SPY_POOL_HPP_INCLUDED

