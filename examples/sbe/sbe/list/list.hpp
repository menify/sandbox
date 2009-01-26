#ifndef SBE_LIST_HPP_INCLUDED
#define SBE_LIST_HPP_INCLUDED

#include "sbe/debug/debug.hpp"

namespace sbe{

template <class T>  class List;

class ListItem
{
    template <class T>  friend class List;

    ListItem*   next_;
    ListItem*   prev_;
    
    ListItem( ListItem const &  list );                // copy is prohibited
    ListItem& operator=( ListItem const &  list );     // copy is prohibited
    
protected:
    inline ListItem( void )
#ifdef SBE_DEBUG
    : next_ (NULL)
    , prev_ (NULL)
#endif
    {}
    
    inline ~ListItem( void )    {}
    
private:
#ifdef SBE_DEBUG
    inline void     init( void )        { this->next_ = NULL; this->prev_ = NULL; }
    inline bool     single( void )      { SBE_ASSERT( this->test() ); return this->next_ == NULL; }
    inline bool     test( void )        { return ((this->next_ == NULL) && (this->prev_ == NULL)) || ((this->next_ != NULL) && (this->prev_ != NULL)); }
#endif
    
    inline void     pushBack( ListItem*  item )
    {
        ListItem* const     item_prev = item->prev_;
        ListItem* const     this_prev = this->prev_;
        
        item->prev_ = this_prev;
        this_prev->next_ = item;
        
        item_prev->next_ = this;
        this->prev_ = item_prev;
    }
    
    //-------------------------------------------------------//
    
    inline void     pop()
    {
        ListItem* const     prev_item = this->prev_;
        ListItem* const     next_item = this->next_;
        
        prev_item->next_ = next_item;
        next_item->prev_ = prev_item;
        
    #ifdef SBE_DEBUG
        this->init();
    #endif
    }
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
        SBE_ASSERT( (item != NULL) && static_cast<ListItem*>(item)->single() );
        SBE_SLOW_ASSERT( this->test() );
        
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
        SBE_SLOW_ASSERT( this->test() );
        
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
        SBE_SLOW_ASSERT( this->linked( item ) );
        
        ListItem*   head = this->head_;
        
        if (head != static_cast<ListItem*>(item))
        {
            static_cast<ListItem*>(item)->pop();
        }
        else
        {
            ListItem*   next = head->next_;
            
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
    bool    linked( ListItem*  item )    const
    {
        SBE_SLOW_ASSERT( this->test() );
        
        ListItem const*  head = this->head_;
        if (head != NULL)
        {
            ListItem const*  it = head;
            
            do
            {
                if (it == item)
                {
                    return true;
                }
                
                it = it->next_;
            }
            while (it != head);
        }
        
        return false;
    }
    
    //-------------------------------------------------------//
    
#ifdef SBE_DEBUG
    bool    test( void )    const
    {
        ListItem const *   next_item;
        ListItem const *   item = this->head_;
        
        if (item != NULL)
        {
            do
            {
                next_item = item->next_;
                
                if (next_item->prev_ != item)
                {
                    return false;
                }
                
                item = next_item;
            }
            while (next_item != this->head_);
        }
        
        return true;
    }
#endif
    
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
    
