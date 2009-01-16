#ifndef SBE_LIST_HPP_INCLUDED
#define SBE_LIST_HPP_INCLUDED

#include "sbe/debug/debug.hpp"

namespace sbe{

template <class T>
class List;

class ListItem
{
    template <class T>  friend class List;

    typedef ListItem    ThisType;

    ThisType*   next_;
    ThisType*   prev_;
    
    ListItem( ThisType const &  list );                // copy is prohibited
    ListItem& operator=( ThisType const &  list );     // copy is prohibited
    
protected:
    inline ListItem( void )    { this->init(); }
    inline ~ListItem( void )   {}
    
private:
    inline void     init( void )    { this->next_ = this; this->prev_ = this; }
    
    inline void     pushBack( ThisType*  item )
    {
    SBE_SLOW_ASSERT( !this->linked( item ) );
    SBE_SLOW_ASSERT( item->test() );

        ThisType* const     item_prev = item->prev_;
        ThisType* const     this_prev = this->prev_;
        
        item->prev_ = this_prev;
        this_prev->next_ = item;
        
        item_prev->next_ = this;
        this->prev_ = item_prev;
    }
    
    //-------------------------------------------------------//
    
    inline void     pushFront( ThisType*  item )
    {
    SBE_SLOW_ASSERT( !this->linked( item ) );
    SBE_SLOW_ASSERT( item->test() );

        ThisType* const     item_prev = item->prev_;
        ThisType* const     this_next = this->next_;
        
        item->prev_ = this;
        this->next_ = item;
        
        item_prev->next_ = this_next;
        this_next->prev_ = item_prev;
    }
    
    //-------------------------------------------------------//
    
    inline void     pop( void )
    {
    SBE_SLOW_ASSERT( this->test() );
        
        ThisType* const     prev_item = this->prev_;
        ThisType* const     next_item = this->next_;
        
        prev_item->next_ = next_item;
        next_item->prev_ = prev_item;
        
        this->init();
    }
    
    //-------------------------------------------------------//
    
    inline bool                 single( void ) const
    {
        return this->next_ == this;
    }
    
    //-------------------------------------------------------//
    
    bool    linked( ThisType*  item )    const
    {
        SBE_SLOW_ASSERT( this->test() );
        
        ThisType const*  it = this ;
        
        do
        {
            if (it == item)
            {
                return true;
            }
            
            it = it->next_;
        }
        while (it != this);
        
        return false;
    }
    
    //-------------------------------------------------------//
    
#ifdef SBE_DEBUG
    bool    test( void )    const
    {
        ThisType const *   next_item;
        ThisType const *   item = this;
        
        if (item == NULL)
        {
            return false;
        }
        
        do
        {
            next_item = item->next_;
            
            if (next_item->prev_ != item)
            {
                return false;
            }
            
            item = next_item;
        }
        while (next_item != this);
        
        return true;
    }
#endif
};

//===========================================================================//

template <class T>
class List
{
    typedef List<T>    ThisType;
    
    //-------------------------------------------------------//
    
    ListItem*   head_;
    
    //-------------------------------------------------------//
    
    List( ThisType const &  list );                // copy is prohibited
    List& operator=( ThisType const &  list );     // copy is prohibited
    
public:
    inline List( void )    : head_( NULL ) {}
    inline ~List( void )   {}
    
    //-------------------------------------------------------//
    
    inline void     pushFront( T*  item )
    {
        SBE_ASSERT( (item != NULL) && item->single() );
        
        ListItem*   head = this->head_;
        
        if (head != NULL)
        {
            head->pushBack( item );
        }
        
        this->head_ = static_cast<ListItem*>(item);
    }
    
    //-------------------------------------------------------//
    
    inline void  pushBack( T*  item )
    {
        SBE_ASSERT( (item != NULL) && static_cast<ListItem*>(item)->single() );
        
        ListItem*   head = this->head_;
        
        if (head != NULL)
        {
            head->pushBack( item );
        }
        else
        {
            this->head_ = static_cast<ListItem*>(item);
        }
    }
    
    //-------------------------------------------------------//
    
    void  pop( T*  item )
    {
        SBE_ASSERT( item != NULL );
        SBE_ASSERT( this->head_ != NULL );
        SBE_SLOW_ASSERT( static_cast<ListItem*>(item)->linked( this->head_ ) );
        
        ListItem*   head = this->head_;
        
        if (head != static_cast<ListItem*>(item))
        {
            static_cast<ListItem*>(item)->pop();
        }
        else
        {
            T*  next = static_cast<T*>(head->next_);
            
            head->pop();
            
            if (head != next)
            {
                this->head_ = next;
            }
            else
            {
                this->head_ = NULL;
            }
        }
    }
    
    //-------------------------------------------------------//
    
    inline T*  popFront( void )
    {
        ListItem*   head = this->head_;
        
        if (head != NULL)
        {
            this->pop( static_cast<T*>(head) );
        }
        
        return static_cast<T*>(head);
    }
    
    //-------------------------------------------------------//
    
    inline T*  popBack( void )
    {
        ListItem*  item = this->head_;
        
        if (item != NULL)
        {
            item = item->prev_;
            this->pop( static_cast<T*>(item) );
        }
        
        return static_cast<T*>(item);
    }
    
    //-------------------------------------------------------//
    
private:
    template <class U>
    U const*  findImpl( U const &  match, ListItem const*  item) const
    {
        ListItem const*    head = this->head_;
        if (head != NULL)
        {
            SBE_SLOW_ASSERT( head->test() );
            SBE_ASSERT( item != NULL );
            
            do
            {
                if (*static_cast<U const*>(item) == match)
                {
                    return static_cast<U const*>(item);
                }
                
                item = item->next_;
            }
            while (item != head);
        }
        
        return NULL;
    }
    
public:
    template <class U>  inline U*           find( U const &  match )            { return const_cast<U*>(const_cast<ThisType const*>(this)->findImpl( match, this->head_ )); }
    template <class U>  inline U const*     find( U const &  match ) const      { return this->findImpl( match, this->head_ ); }
    
    template <class U>  inline U const*     findNext( U const &  match, U const*  item) const   { return this->findImpl( match, item ); }
    template <class U>  inline U*           findNext( U const &  match, U*  item) const         { return const_cast<U*>(const_cast<ThisType const*>(this)->findImpl( match, item )); }
    
    //-------------------------------------------------------//
    
    inline T*           front( void )           { return static_cast<T*>(this->head_); }
    inline T const *    front( void ) const     { return static_cast<T*>(this->head_); }
    inline T *          back( void )            { return (this->head_ != NULL) ? static_cast<T*>(this->head_->prev_) : NULL; }
    inline T const *    back( void ) const      { return (this->head_ != NULL) ? static_cast<T*>(this->head_->prev_) : NULL; }
};

}   // namespace spy

#endif  //  #ifndef SBE_LIST_HPP_INCLUDED  //
    
