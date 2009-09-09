#ifndef ANL_LOG_MESSAGE_HPP_INCLUDED
#define ANL_LOG_MESSAGE_HPP_INCLUDED

#include <map>
#include <string>
#include <boost/shared_ptr.hpp>

namespace anl
{

class LogMessage
{
//=======================================================//
// public types
public:
  class AttributeValueBase
  {
  protected:
      inline AttributeValueBase( void )    {}
      virtual ~AttributeValueBase( void )  {} = 0;
      
      virtual String const &   getString() const;
  };
  
  //-------------------------------------------------------//
  
  typedef std::string                                       String;
  typedef std::string                                       AttributeName;
  typedef boost::shared_ptr<AttributeValueBase>             AttributeValuePtr;
  typedef std::map<const AttributeName, AttributeValuePtr>  Attributes;
  typedef iterator                                          Attributes::iterator;
  typedef const_iterator                                    Attributes::const_iterator;

//=======================================================//
// public methods
public:
  inline  ~LogMessage( void ) {}
  inline  LogMessage( void ) : attributes_() {}
  
  inline LogMessage( LogMessage const &  other )
  : attributes_(other.attributes_)
  {}
  
  inline LogMessage&  operator=( LogMessage const &  other )
  {
    this->attributes_ = other.attributes_;
    return *this;
  }
  
  inline AttributeValuePtr&         operator[](AttributeName const &   name)        { return this->attributes_[name]; }
  inline AttributeValuePtr const &  operator[](AttributeName const &   name) const  { return this->attributes_[name]; }
  
  inline iterator         begin( void )       { return this->attributes_.begin(); }
  inline const_iterator   begin( void ) const { return this->attributes_.begin(); }
  inline iterator         end( void )         { return this->attributes_.end(); }
  inline const_iterator   end( void ) const   { return this->attributes_.end(); }
  
  inline void             clear( void )       { this->attributes_.clear(); }

private:
  Attributes    attributes_;
};

} // namespace anl

#endif  // ANL_LOG_MESSAGE_HPP_INCLUDED
