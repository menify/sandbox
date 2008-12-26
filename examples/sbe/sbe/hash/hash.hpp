#ifndef SPY_HASH_HPP_INCLUDED
#define SPY_HASH_HPP_INCLUDED

#include <stddef.h>

#include "sbe/list/intrusive_list.hpp"

namespace sbe{

//---------------------------------------------------------------------------//

class HashItem: public IntrusiveList<HashItem>
{
protected:
    inline HashItem( void ) : IntrusiveList<HashItem>() {}
    inline ~HashItem( void ) {}
};

//---------------------------------------------------------------------------//

template <class T, size_t  t_table_size >
class Hash
{
private:
    typedef Hash<T, t_table_size>   ThisType;
    typedef HashItem                Item;
    
    
    T*  table_[ t_table_size ];
    
    //-------------------------------------------------------//
    
    Hash( ThisType const &   hash );                // no copy
    Hash&   operator=( ThisType const &   hash );   // no copy
public:
    
    //-------------------------------------------------------//
    
    inline Hash( void )
    {
        for (size_t  i = 0; i < t_table_size; ++i)
        {
            this->table_[i] = NULL;
        }
    }
    
    //-------------------------------------------------------//
    
    inline ~Hash( void )
    {}
    
    //-------------------------------------------------------//
    
    void    insert( T*  item )
    {
        SBE_ASSERT( item != NULL );
        SBE_ASSERT( this->get( *item ) == NULL );
        SBE_ASSERT( item->single() );
        
        listPushFront( this->head( item ), item );
    }
    
    //-------------------------------------------------------//
    
    void    remove( T*  item )
    {
        SBE_ASSERT( this->get( *item ) == item );
        
        T** const     p_head = this->head( item );
        
        if (*p_head == item)
        {
            if (static_cast<Item*>(item)->single())
            {
                *p_head = NULL;
                return;
            }
            else
            {
                *p_head = static_cast<T*>(static_cast<Item*>(item)->next());
            }
        }
        
        static_cast<Item*>(item)->pop();
    }
    
    //-------------------------------------------------------//
    
    T const *   get( T const &  match_item ) const
    {
        T const * const     head_item = *this->head( &match_item );
        
        if (head_item == NULL)
        {
            return NULL;
        }
        
        T const*  item = head_item;
        
        do
        {
            if (*item == match_item)
            {
                return item;
            }
            
            item = static_cast<T const*>(static_cast<Item const*>(item)->next());
        }
        while( item != head_item );
        
        return NULL;
    }
    
    inline T*   get( T const&  match_item )
    {
        return const_cast<T*>(const_cast<ThisType const*>(this)->get( match_item ));
    }
    
    //-------------------------------------------------------//
    
private:
    inline T**    head( T*  item )
    {
        return &this->table_[ hashKey( item ) % t_table_size ];
    }
    
    inline T const* const *     head( T const *  item ) const
    {
        return &this->table_[ hashKey( item ) % t_table_size ];
    }
};

//---------------------------------------------------------------------------//

} // namespace sbe

#endif //   #ifndef SPY_HASH_HPP_INCLUDED
