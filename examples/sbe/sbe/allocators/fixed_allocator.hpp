#ifndef SBE_FIXED_ALLOCATOR_HPP_INCLUDED
#define SBE_FIXED_ALLOCATOR_HPP_INCLUDED

#include <stddef.h>

#include "sbe/compile_time/static_algorithm.hpp"
#include "sbe/ut/debug.hpp"


namespace sbe{

//---------------------------------------------------------------------------//

/*
    Class: FixedAllocator
    Allocates items from the fixed memory buffer.
    
    Parameters:
        T           - a type of allocated items
        t_alignment - an alignment of allocated items
*/
template <typename T, size_t  t_alignment = sizeof(T*) >
class FixedAllocator
{
public:
    typedef size_t      size_type;
    typedef ptrdiff_t   difference_type;
    typedef T*          pointer;
    typedef const T*    const_pointer;
    typedef T&          reference;
    typedef const T&    const_reference;
    typedef T           value_type;
    
    //-------------------------------------------------------//
private:
    struct Node
    {
        Node*   next;
    };
    
    enum
    {
        alignment_ = StaticMax< t_alignment, sizeof(Node*) >::result,
        aligned_value_size_ = (sizeof(T) + (alignment_ - 1)) & (~(alignment_ - 1))
    };
    
    typedef FixedAllocator<T, t_alignment>      ThisType;
    
    Node    nodes_list_;
    
#ifdef SBE_DEBUG
    void*       aligned_buf_;
    size_type   aligned_buf_size_;
#endif
    
    //-------------------------------------------------------//
    
    inline FixedAllocator( ThisType const & );          // no copy
    inline ThisType&    operator=( ThisType const &);   // no copy
    
public:
    
    FixedAllocator( void*  buf, size_type  buf_size )
    {
        unsigned char*          node = reinterpret_cast<unsigned char*>((reinterpret_cast<size_type>(buf) + (alignment_ - 1)) & (~(alignment_ - 1)));
        unsigned char* const    end  = static_cast<unsigned char*>(buf) + buf_size;
        
    #ifdef SBE_DEBUG
        this->aligned_buf_ = node;
        
        size_type       aligned_buf_size = reinterpret_cast<size_type>(this->aligned_buf_) - reinterpret_cast<size_type>(buf);
        if (aligned_buf_size < buf_size)
        {
            aligned_buf_size = buf_size - aligned_buf_size;
        }
        else
        {
            aligned_buf_size = 0;
        }
        
        this->aligned_buf_size_ = (aligned_buf_size / aligned_value_size_) * aligned_value_size_;
    #endif
        
        
        
        Node*           prev_node = &this->nodes_list_;
        
        for (unsigned char* next_node = node + aligned_value_size_; next_node <= end; next_node += aligned_value_size_ )
        {
            prev_node->next = reinterpret_cast<Node*>(node);
            prev_node = reinterpret_cast<Node*>(node);
            node = next_node;
        }
        
        prev_node->next = NULL;
    }
    
    //-------------------------------------------------------//
    
    ~FixedAllocator( void ){}
    
    //-------------------------------------------------------//
    
    inline pointer      allocate( void )
    {
    SBE_ASSERT( this->test() );
    
        Node*   node = this->nodes_list_.next;
        if (node != NULL)
        {
            this->nodes_list_.next = node->next;
        }
        
        return reinterpret_cast<pointer>(node);
    }
    
    //-------------------------------------------------------//
    
    inline void    deallocate( pointer p )
    {
        if (p == NULL) return;
    
    SBE_ASSERT( this->chekNode( p ) );
    SBE_ASSERT( this->test() );
    
        Node*   node = reinterpret_cast<Node*>(p);
        node->next = this->nodes_list_.next;
        this->nodes_list_.next = node;
    }
    
    //-------------------------------------------------------//
private:
#ifdef SBE_DEBUG
    bool    chekNode( void const *  node )    const
    {
        size_type const  node_offset = reinterpret_cast<size_type>(node) - reinterpret_cast<size_type>(this->aligned_buf_);
        return (node_offset < this->aligned_buf_size_) && ((node_offset % aligned_value_size_) == 0);
    }
#endif  // ifdef SBE_DEBUG
    
    //-------------------------------------------------------//
public:
#ifdef SBE_DEBUG
    bool    test( void ) const
    {
        size_type       count = 0;
        size_type const total = this->aligned_buf_size_ / aligned_value_size_;
        
        for (Node const *  node = this->nodes_list_.next; node != NULL; node = node->next )
        {
            if (count == total)
            {
                return false;
            }
            
            ++count;
            
            if (!this->chekNode(node))
            {
                return false;
            }
        }
        
        return true;
    }
#endif  // ifdef SBE_DEBUG
};

//---------------------------------------------------------------------------//

}   // namespace sbe

#endif  //  #ifndef SBE_FIXED_ALLOCATOR_HPP_INCLUDED  //
