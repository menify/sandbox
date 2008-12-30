#ifndef SPY_HASH_HPP_INCLUDED
#define SPY_HASH_HPP_INCLUDED

#include <stddef.h>

#include "sbe/list/list.hpp"

namespace sbe{

//---------------------------------------------------------------------------//

class HashItem: public ListItem<HashItem>
{
protected:
    inline HashItem( void ) : ListItem<HashItem>() {}
    inline ~HashItem( void ) {}
};


//---------------------------------------------------------------------------//

template <class T, size_t  t_table_size >
class Hash
{
private:
    typedef Hash<T, t_table_size>   ThisType;
    typedef HashItem                Item;
    typedef List<HashItem>          Head;
    
    
    Head    table_[ t_table_size ];
    
    //-------------------------------------------------------//
    
    Hash( ThisType const &   hash );                // no copy
    Hash&   operator=( ThisType const &   hash );   // no copy
public:
    
    //-------------------------------------------------------//
    
    inline Hash( void )     {}
    inline ~Hash( void )    {}
    
    //-------------------------------------------------------//
    
    inline void     insert( T*  item )
    {
        SBE_ASSERT( item != NULL );
        SBE_ASSERT( this->get( *item ) == NULL );
        
        this->head( *item )->pushFront( item );
    }
    
    //-------------------------------------------------------//
    
    inline void     remove( T*  item )
    {
        SBE_ASSERT( this->get( *item ) == item );
        
        this->head( *item )->pop( item );
    }
    
    //-------------------------------------------------------//
    
    inline T const *   get( T const &  match_item ) const
    {
        return this->head( match_item )->find( match_item );
    }
    
    inline T*   get( T const&  match_item )
    {
        return const_cast<T*>(const_cast<ThisType const*>(this)->get( match_item ));
    }
    
    //-------------------------------------------------------//
    
private:
    inline Head*    head( T const &  item )
    {
        return const_cast<Head*>( const_cast<ThisType const*>(this)->head( item ) );
    }
    
    inline Head const*  head( T const &  item ) const
    {
        return &this->table_[ hashKey( item ) % t_table_size ];
    }
};

//---------------------------------------------------------------------------//

} // namespace sbe

#endif //   #ifndef SPY_HASH_HPP_INCLUDED
