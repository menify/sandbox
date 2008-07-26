#ifndef SBE_DELETERS_HPP_INCLUDED
#define SBE_DELETERS_HPP_INCLUDED


namespace sbe{

/* Title: Deleters
    Some generic functors to destroy objects.
    They are designed to be used with a smart pointers.
*/

//---------------------------------------------------------------------------//

/*
    Class: NewDeleter
    This functor implements operator 'delete' srategy.
    It may be used to free objects which were allocated by operator 'new'.
    It's designed to be passed to a smart pointer (like <AutoPtr> or <SafePtr>).
*/
template <typename T>
struct NewDeleter
{
    inline void      operator()( T*  ptr )       { delete ptr; }
};

//---------------------------------------------------------------------------//

/*
    Class: NewArrayDeleter
    This functor implements operator 'delete[]' srategy.
    It may be used to free objects which were allocated by operator 'new[]'.
    It's designed to be passed to a smart pointer (like <AutoPtr> or <SafePtr>).
*/
template <typename T>
struct NewArrayDeleter
{
    inline void      operator()( T*  ptr )       { delete[] ptr; }
};

//---------------------------------------------------------------------------//

/*
    Class: PlacementNewDeleter
    This is functor class implements a call of destructor srategy.
    If an object was created via a operator placement new then to destroy this object
    we should call its destructor only.
    It's may be passed to a smart pointer (like <AutoPtr> or <SafePtr>).
*/
template <typename T>
struct PlacementNewDeleter
{
    inline void      operator()( T*  ptr )       { if (ptr != NULL) ptr->~T(); }
};

}   // namespace sbe

#endif  //  #ifndef SBE_DELETERS_HPP_INCLUDED  //
