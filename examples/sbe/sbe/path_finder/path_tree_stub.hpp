#ifndef PATH_TREE_HPP_INCLUDED
#define PATH_TREE_HPP_INCLUDED


namespace sbe{

//===========================================================================//

template <typename T>
class   PathTreeStub
{
    typedef PathTreeStub    ThisType;
    
public:
    class   iterator
    {
        typedef iterator    ThisType;
        
        T   obj_;
    
    public:
        inline ~iterator( void )        {}
        inline iterator( void ) : T()   {}
        
        inline explicit iterator( T const &  obj ) : obj_( obj )    {}
        inline iterator( ThisType const &  it ) : obj_( it.obj_ )   {}
        
        inline ThisType&    operator=( ThisType const &  it )       //lint --e{1529}    // Warning -- Symbol not first checking for assignment to this
        {
            this->obj_ = it.obj_;
            return *this;
        }
        
        //-------------------------------------------------------//
        
        inline T&               operator*( void )           { return this->obj_; }
        inline T const&         operator*( void )  const    { return this->obj_; }
        
        inline T *              operator->( void )          { return &this->obj_; }
        inline T const *        operator->( void )  const   { return &this->obj_; }
    };
    
    inline ThisType&   operator=( ThisType const &) {}
    inline PathTreeStub( ThisType const &)          {}
    inline PathTreeStub( void )                     {}
    inline ~PathTreeStub( void )                    {}
    
    //-------------------------------------------------------//
    
    inline iterator     attach( T const &  obj )
    {
        return iterator( obj );
    }
    
    //-------------------------------------------------------//
    
    inline iterator     attach( T const &  obj, iterator const &, size_t)
    {
        return iterator( obj );
    }
    
    //-------------------------------------------------------//
    
    inline void    collapse( iterator const &) { }
    
    //-------------------------------------------------------//
};

//===========================================================================//

}   // namespace sbe

#endif  // #ifndef PATH_TREE_HPP_INCLUDED
