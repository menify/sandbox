#ifndef SBE_INTRUSIVE_LIST_HPP_INCLUDED
#define SBE_INTRUSIVE_LIST_HPP_INCLUDED

#include "sbe/ut/debug.hpp"

namespace sbe{

template <typename T>
class ListItem
{
    typedef ListItem<T>    ThisType;

    ThisType*   next_;
    ThisType*   prev_;
    
    ListItem( ThisType const &  list );                // copy is prohibited
    ListItem& operator=( ThisType const &  list );     // copy is prohibited
    
protected:
    inline ListItem( void )    { this->init(); }
    inline ~ListItem( void )   {}
    
private:
    inline void     init( void )    { this->next_ = this; this->prev_ = this; }
    
public:
    inline void     pushBack( ThisType*  item )
    {
    SBE_ASSERT( !this->linked( item ) );
    SBE_ASSERT( item->test() );

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
    SBE_ASSERT( !this->linked( item ) );
    SBE_ASSERT( item->test() );

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
    SBE_ASSERT( this->test() );
        
        ThisType* const     prev_item = this->prev_;
        ThisType* const     next_item = this->next_;
        
        prev_item->next_ = next_item;
        next_item->prev_ = prev_item;
        
        this->init();
    }
    
    //-------------------------------------------------------//
    
    inline bool         single( void ) const        { return this->next_ == this; }
    inline T const *    next( void ) const          { return static_cast<T const *>(this->next_); } //lint !e1939   //Note -- Down cast detected
    inline T *          next( void )                { return static_cast<T*>(this->next_); }        //lint !e1939   //Note -- Down cast detected
    inline T const *    previous( void ) const      { return static_cast<T const*>(this->prev_); }  //lint !e1939   //Note -- Down cast detected
    inline T *          previous( void )            { return static_cast<T*>(this->prev_); }        //lint !e1939   //Note -- Down cast detected
    
    //-------------------------------------------------------//
    
    bool    linked( ThisType*  item )    const
    {
        SBE_ASSERT( this->test() );
        
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
    
    template <class U>
    U const*  find( U const &  match ) const
    {
        SBE_ASSERT( this->test() );
        
        ThisType const*  it = this ;
        
        do
        {
            if (*static_cast<U const*>(it) == match)
            {
                return static_cast<U const*>(it);
            }
            
            it = it->next_;
        }
        while (it != this);
        
        return NULL;
    }
    
    template <class U>
    inline U*  find( U const &  match )
    {
        return const_cast<U*>(const_cast<ThisType const *>(this)->find( match ));
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
    
    T*  head_;
    
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
        
        T*  head = this->head_;
        
        if (head != NULL)
        {
            head->pushBack( item );
        }
        
        this->head_ = item;
    }
    
    //-------------------------------------------------------//
    
    inline void  pushBack( T*  item )
    {
        SBE_ASSERT( (item != NULL) && item->single() );
        
        T*  head = this->head_;
        
        if (head != NULL)
        {
            head->pushBack( item );
        }
        else
        {
            this->head_ = item;
        }
    }
    
    //-------------------------------------------------------//
    
    void  pop( T*  item )
    {
        SBE_ASSERT( item != NULL );
        SBE_ASSERT( this->head_ != NULL );
        SBE_ASSERT( item->linked( this->head_ ) );
        
        T*  head = this->head_;
        
        if (head != item)
        {
            item->pop();
        }
        else
        {
            T*  next = head->next();
            
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
        T*  item = this->head_;
        
        if (item != NULL)
        {
            this->pop( item );
        }
        
        return item;
    }
    
    //-------------------------------------------------------//
    
    inline T*  popBack( void )
    {
        T*  item = this->head_;
        
        if (item != NULL)
        {
            item = item->previous();
            this->pop( item );
        }
        
        return item;
    }
    
    //-------------------------------------------------------//
    
    template <class U>
    inline U const*  find( U const & match ) const
    {
        T const*    head = this->head_;
        if (head != NULL)
        {
            return head->find( match );
        }
        
        return NULL;
    }
    
    template <class U>
    inline U*  find( U const & match )
    {
        return const_cast<U*>(const_cast<ThisType const*>(this)->find( match ));
    }
    
    //-------------------------------------------------------//
    
    inline T*           front( void )           { return this->head_; }
    inline T const *    front( void ) const     { return this->head_; }
    inline T *          back( void )            { return (this->head_ != NULL) ? this->head_->previous() : NULL; }
    inline T const *    back( void ) const      { return (this->head_ != NULL) ? this->head_->previous() : NULL; }
};

}   // namespace spy

#endif  //  #ifndef SBE_INTRUSIVE_LIST_HPP_INCLUDED  //
    
