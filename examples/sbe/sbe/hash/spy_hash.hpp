#ifndef SPY_HASH_HPP_INCLUDED
#define SPY_HASH_HPP_INCLUDED

#include <stddef.h>

namespace sbe{
namespace spy{

//---------------------------------------------------------------------------//

template <typename T, size_t  t_table_size >
class Hash
{
public:
    struct Item: public IntrusiveList<Item>
    {};

private:
    typedef Hash<T, t_table_size>   ThisType;
    
    
    T*  table_[ t_table_size ];
    
    //-------------------------------------------------------//
    
    Hash( ThisType const &   hash );                // no copy
    Hash&   operator=( ThisType const &   hash );   // no copy
public:
    
    //-------------------------------------------------------//
    
    inline Hash( void )
    {
        for (size_t  i = 0; i < this->size_; ++i)
        {
            this->table_[i] = NULL;
        }
    }
    
    //-------------------------------------------------------//
    
    inline ~Hash( void )
    {}
    
    //-------------------------------------------------------//
    
    void    insertBack( T*  item )
    {
        T** const   p_head = this->head( item );
        
        if (*p_head != NULL)
        {
            static_cast<Item*>((*p_head))->pushBack( item );
        }
        
        *p_head = item;
    }
    
    //-------------------------------------------------------//
    
    void    insertFront( T*  item )
    {
        T** const   p_head = this->head( item );
        
        if (*p_head != NULL)
        {
            static_cast<Item*>((*p_head))->pushFront( item );
        }
        
        *p_head = item;
    }
    
    //-------------------------------------------------------//
    
    void    remove( T*  item )
    {
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
                *p_head = static_cast<Item*>(item)->next();
            }
        }
        
        static_cast<Item*>(item)->pop();
    }
    
    //-------------------------------------------------------//
    
    T*      get( T*    match_item )
    {
        T* const      head_item = *this->head( ptr );
        
        if (head_item == NULL)
        {
            return NULL;
        }
        
        T*  item = head_item;
        
        do
        {
            if (*item == *match_item)
            {
                return item;
            }
            
            item = static_cast<Item*>(item)->next();
        }
        while( item != head_item );
        
        return NULL;
    }
    
    //-------------------------------------------------------//
    
private:
    inline T**      head( T const *  item )
    {
        return &this->table_[ hashKey( item ) % t_table_size ];
    }
};

//---------------------------------------------------------------------------//

} // namespace spy
} // namespace sbe

#endif //   #ifndef SPY_HASH_HPP_INCLUDED
