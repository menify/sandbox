#ifndef SBE_POSITION_HPP_INCLUDED
#define SBE_POSITION_HPP_INCLUDED

#include <stddef.h>
#include <vector>
#include <queue>
#include <algorithm>

namespace sbe{

//inline bool                      isOccupied( Level::Position const &  pos ) const;
//inline Level::Position const &   manPos( void ) const;
//inline Level::Size const &       size( void ) const;
//inline Level::Position const*    directionVectors( void ) const;
//inline enum Level::directions

//inline enum Level::DirectionEnumerator
//inline enum Level::StepDirector( size_t  start_index );


template <class TLevel, template <class> class TAllocator = std::allocator>
class   PathFinder
{
    typedef unsigned char                           Cell;
    typedef std::vector< Cell, TAllocator<Cell> >   Row;
    typedef std::vector< Row, TAllocator<Cell> >    Table;
    
    typedef typename TLevel::Position               Position;
    typedef typename TLevel::Positions              Positions;
    
    typedef typename TLevel::Size                   Size;
    
    typedef PathFinder< TLevel, TAllocator >        ThisType;
    
    //-------------------------------------------------------//
    
    enum
    {
          MAN_FRONT_BITS = 2
        , MAN_FRONT_MASK = ((1 << MAN_FRONT_BITS) - 1)
        , MAN_FRONTS = (1 << MAN_FRONT_BITS) - 1
        , BOX_SHIFT = MAN_FRONT_BITS
        , BOX_BITS = TLevel::directions
        , BOX_MASK = ((1 << BOX_BITS) - 1) << BOX_SHIFT
        , PATH_DIRECTIONS = TLevel::directions
    };
    
    //-------------------------------------------------------//
    
    TLevel const* const     level_;
    Table                   table_;
    Positions               path_;
    Positions               occupied_;
    Positions               vacant_;
    
    //-------------------------------------------------------//
    
public:
    
    inline ~PathFinder( void )  {}
    
    //-------------------------------------------------------//
    
    PathFinder( TLevel const *  level )
        : level_( level )
        , table_(),
        , path_()
        , occupied_()
        , vacant_()
    {
        Row const       row( level->size().width, Cell );
        this->table_.assign( level->size().height, row );
    }
    
    //-------------------------------------------------------//
    
    size_t      resetTable( void )
    {
        Table::iterator const   row_begin = this->table_.begin();
        Table::iterator const   row_end = this->table_.end();
        
        for (Table::iterator  row = row_begin; row < row_end; ++row)
        {
            std::fill( row.begin(), row.end(), MAN_FRONTS );
        }
    }
    
    //-------------------------------------------------------//
    
    size_t      resetManTable( void )
    {
        Table::iterator const   row_begin = this->table_.begin();
        Table::iterator const   row_end = this->table_.end();
        
        for (Table::iterator  row = row_begin; row < row_end; ++row)
        {
            Row::iterator const     cell_begin  = row->begin();
            Row::iterator const     cell_end    = row->end();
            
            for (Row::iterator  cell = cell_begin; cell < cell_end; ++cell)
            {
                *cell |= MAN_FRONTS;
            }
        }
    }
    
    //-------------------------------------------------------//
    
    size_t      manPath( Position const &  start, Position const &  finish )
    {
        
    }
    
    //-------------------------------------------------------//
    

private:
    Cell*       cell( Position const &  pos )
    {
    SBE_ASSERT( pos.y() < this->table_.size() );
    SBE_ASSERT( pos.x() < this->table_[0].size() );
        
        return &this->table_[ pos.y() ][ pos.x() ];
    }
    
    //-------------------------------------------------------//
    
    bool        isOccupied( Position const &  pos ) const
    {
        if (this->level_->isOccupied( pos ))
        {
            Positions::const_iterator const     vacant_end = this->vacant_.end();
            
            Positions::const_iterator const     it = std::find( this->vacant_.begin(), vacant_end, pos );
            if (it == vacant_end)
            {
                return true;
            }
        }
        
        Positions::const_iterator const     occupied_end = this->occupied_.end();
        
        Positions::const_iterator const     it = std::find( this->occupied_.begin(), occupied_end, pos );
        if (it != occupied_end)
        {
            return true;
        }
        
        return false;
    }
    
    //-------------------------------------------------------//
    
    static inline void      manStep( Cell*  step_cell, Cell  front )
    {
    SBE_ASSERT( front < MAN_FRONTS );
    SBE_ASSERT( ((*step_cell) & MAN_FRONT_MASK) == MAN_FRONTS);
        
        *step_cell &= (~MAN_FRONT_MASK) | front;
    }
    
    //-------------------------------------------------------//
    
    static inline bool      manFrontVisited( Cell*  step_cell, Cell  front )
    {
    SBE_ASSERT( front < MAN_FRONTS );
        
        return (*step_cell & MAN_FRONT_MASK) == front;
    }
    
    //-------------------------------------------------------//
    
    static inline bool      manVisited( Cell*  step_cell )
    {
        return ((*step_cell & MAN_FRONT_MASK) != MAN_FRONTS);
    }
    
    //-------------------------------------------------------//
    
    struct ManPathData
    {
        Position const      pos;
        size_t const        direction;
    };
    
    typedef PathTree<ManPathData>   ManPath;
    typedef std::vector< ManPath::iterator >    ManPathFront;

    typedef PathTreeStub<Position>  ManPathStub;
    typedef std::vector< ManPathStub::iterator >    ManPathStubFront;

    size_t      manPathSize(
        
        Position const &    start,
        Position const &    finish
    )
    {
        typedef std::vector< Position, TAllocator< Position > >     Front;
        
        struct  FrontData
        {
            Front   current;
            Front   next;
        };
        
        if (start == finish)
        {
            return 0;
        }
        
        this->resetManTable();
        
        FrontData       fronts[ MAN_FRONTS ];
        
        front[0].current.push_back( start );
        front[1].current.push_back( finish );
        
        //-------------------------------------------------------//
        
        size_t      path_size = 1;      // it's at least 1, because start != finish
        
        -1 2
        
        5 + -1
        5 + -1 - (-1) + 1
        
         1,  0       1,  0     4,7
        -1,  0      -2,  0     2,7
         0,  1       1,  1     3,8
         0, -1       0, -2     3,6
         
        -1,  0      -1,  0     2,7
         0,  1       1,  1     3,8
         0, -1       0, -2     3,6
         1,  0       1,  1     4,7
         
         0,  1       0,  1     3,8
         0, -1       0, -2     3,6
         1,  0       1,  1     4,7
        -1,  0      -2,  0     2,7
        
         0, -1       0, -1     3,6
         1,  0       1,  1     4,7
        -1,  0      -2,  0     2,7
         0,  1       1,  1     3,8
        
         3, 7
         2, 7
         4, 8
         2, 6
        
        for (;;)
        {
            for (Cell   front = 0; front < MAN_FRONTS; ++front, ++path_size)
            {
                Front*  current_front = fronts[ front ];
                
                Front::const_iterator   end = current_front->current.end();
                
                for (Front::const_iterator  step = current_front->current.begin(); step != end; ++step)
                {
                    for (TLevel::Navigator   pos( *step ); pos.moving(); pos.move() )
                    {
                        Cell*   step_cell = this->cell( pos );
                        
                        if ((!this->manFrontVisited( step_cell, front )) && (!this->isOccupied( pos )))
                        {
                            if (this->manVisited( step_cell ))      // finished
                            {
                                return path_size;
                            }
                            
                            manStep( step_cell, front );
                            
                            current_front->next.push_back(  pos );
                        }
                    }
                }
                
                if (current_front->next.empty())
                {
                    return -1;
                }
                
                current_front->current.clear();
                
                std::swap( current_front->current, current_front->next );
            }
        }
    }
};



}   // namespace sbe

#endif  //  #ifndef SBE_POSITION_HPP_INCLUDED
