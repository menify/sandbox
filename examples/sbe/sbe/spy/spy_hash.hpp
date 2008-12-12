#ifndef SPY_HASH_HPP_INCLUDED
#define SPY_HASH_HPP_INCLUDED

#include <stddef.h>

namespace sbe{
namespace spy{

//---------------------------------------------------------------------------//

template <typename T>
class Hash
{
        PtrList** const table_;
        size_t          size_;
        size_t          shift_size_;
    
    public:
        
        struct List: public IntrusiveList<T>
        {};
        
        
        Hash( void*     heap, size_t  heap_size, size_t  shift_size );
        inline ~Hash( void )    {}
        
        
        void    push( T*    item );
        void    pop( T*     item );
        
        PtrList*      get( void const *  ptr );
        
    private:
        
        inline size_t    index( void const *  ptr )     const
        {
            return (reinterpret_cast<size_t>(ptr) >> this->shift_size_) % this->size_;
        }
        
        inline PtrList**    head( void const *  ptr )  { return &this->table_[ this->index( ptr ) ]; }
        
        Hash( Hash const &   hash );                    // no copy
        Hash&   operator=( Hash const &   hash );   // no copy
};

//---------------------------------------------------------------------------//

} // namespace spy
} // namespace sbe

#endif //   #ifndef SPY_HASH_HPP_INCLUDED
