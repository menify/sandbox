#ifndef SBE_INTRUSIVE_LIST_HPP_INCLUDED
#define SBE_INTRUSIVE_LIST_HPP_INCLUDED

#include "sbe/ut/debug.hpp"

namespace sbe{

template <typename T>
class IntrusiveList
{
    typedef IntrusiveList<T>    ThisType;

    ThisType*   next_;
    ThisType*   prev_;
    
    IntrusiveList( ThisType const &  list );                // copy is prohibited
    IntrusiveList& operator=( ThisType const &  list );     // copy is prohibited
    
protected:
    inline IntrusiveList( void )    { this->init(); }
    inline ~IntrusiveList( void )   {}
    
    inline void     init( void )    { this->next_ = this; this->prev_ = this; }
    
public:
    inline void     pushBack( ThisType*  item );
    inline void     pushFront( ThisType*  item );
    inline void     pop( void );
    
    inline bool         single( void ) const        { return this->next_ == this; }
    inline T const *    next( void ) const          { return static_cast<T const *>(this->next_); } //lint !e1939   //Note -- Down cast detected
    inline T *          next( void )                { return static_cast<T*>(this->next_); }        //lint !e1939   //Note -- Down cast detected
    inline T const *    previous( void ) const      { return static_cast<T const*>(this->prev_); }  //lint !e1939   //Note -- Down cast detected
    inline T *          previous( void )            { return static_cast<T*>(this->prev_); }        //lint !e1939   //Note -- Down cast detected
    
    //-------------------------------------------------------//
    
#ifdef SBE_DEBUG
    bool    test( void )    const;
#endif
};

//===========================================================================//

template <typename T>
inline void     IntrusiveList<T>::pushBack(
    
    ThisType*   item
)
{
SBE_ASSERT( this->test() );
SBE_ASSERT( item->test() );

    ThisType* const     item_prev = item->prev_;
    ThisType* const     this_prev = this->prev_;
    
    item->prev_ = this_prev;
    this_prev->next_ = item;
    
    item_prev->next_ = this;
    this->prev_ = item_prev;
}

/*
1 -> 2 -> 3
  <-   <-

4 -> 5 -> 6
  <-   <-

1*-> 5 -> 6 -> 4*-> 2 -> 3
 *<-   <-   <-  *<-   <-
*/

//---------------------------------------------------------------------------//

template <typename T>
inline void     IntrusiveList<T>::pushFront(
    
    ThisType*   item
)
{
SBE_ASSERT( this->test() );
SBE_ASSERT( item->test() );

    ThisType* const     item_prev = item->prev_;
    ThisType* const     this_next = this->next_;
    
    item->prev_ = this;
    this->next_ = item;
    
    item_prev->next_ = this_next;
    this_next->prev_ = item_prev;
}

//---------------------------------------------------------------------------//

template <typename T>
inline void     IntrusiveList<T>::pop( void )
{
SBE_ASSERT( this->test() );
    
    ThisType* const     prev_item = this->prev_;
    ThisType* const     next_item = this->next_;
    
    prev_item->next_ = next_item;
    next_item->prev_ = prev_item;
    
    this->init();
}

//---------------------------------------------------------------------------//

#ifdef SBE_DEBUG
template <typename T>
bool     IntrusiveList<T>::test( void )     const
{
    ThisType const *   next_item;
    ThisType const *   item = this;
    
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
#endif  // #ifdef SBE_DEBUG


}   // namespace spy

#endif  //  #ifndef SBE_INTRUSIVE_LIST_HPP_INCLUDED  //
