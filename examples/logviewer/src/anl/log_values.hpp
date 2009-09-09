#ifndef ANL_LOG_MESSAGE_HPP_INCLUDED
#define ANL_LOG_MESSAGE_HPP_INCLUDED

#include <stddef.h>
#include <boost/lexical_cast.hpp>
#include "boost/date_time/posix_time/posix_time.hpp"

#include "anl/log_message.hpp"

//===========================================================================//

namespace anl
{

//---------------------------------------------------------------------------//

class AttributeValueString: public LogMessage::AttributeValueBase
{
public:
    explicit inline AttributeValueString( LogMessage::String const &  value )
    : value_( value )
    {}
    
    virtual ~AttributeValueString( void )  {};
    
    virtual LogMessage::String const &   getString() const { return value_; }

private:
  LogMessage::String    value_;
};

//---------------------------------------------------------------------------//

class AttributeValueInt: public LogMessage::AttributeValueBase
{
public:
    explicit inline AttributeValueInt( ptrdiff_t  value )
    : value_( value )
    , str_value_( boost::lexical_cast<LogMessage::String>(value) )
    {}
    
    virtual ~AttributeValueInt( void )  {}
    
    virtual LogMessage::String const &   getString() const { return str_value_; }

private:
  ptrdiff_t             value_;
  LogMessage::String    str_value_;
};

class AttributeValueHexInt: public LogMessage::AttributeValueBase
{
public:
    explicit inline AttributeValueHexInt( ptrdiff_t  value )
    : value_( value )
    , str_value_( boost::lexical_cast<LogMessage::String>(value) )  // TODO: need to convert to hex format
    {}
    
    virtual ~AttributeValueInt( void )  {}
    
    virtual LogMessage::String const &   getString() const { return str_value_; }

private:
  ptrdiff_t             value_;
  LogMessage::String    str_value_;
};

//---------------------------------------------------------------------------//

class AttributeValueSize: public LogMessage::AttributeValueBase
{
public:
    explicit inline AttributeValueSize( size_t  value )
    : value_( value )
    , str_value_( boost::lexical_cast<LogMessage::String>(value) )
    {}
    
    virtual ~AttributeValueSize( void )  {}
    
    virtual LogMessage::String const &   getString() const { return str_value_; }

private:
  size_t                value_;
  LogMessage::String    str_value_;
};

//---------------------------------------------------------------------------//

class AttributeValueTime: public LogMessage::AttributeValueBase
{
public:
    explicit inline AttributeValueTime( boost::posix_time::ptime  value )
    : value_( value )
    , str_value_( boost::posix_time::to_simple_string(value) )
    {}
    
    virtual ~AttributeValueTime( void )  {}
    
    virtual LogMessage::String const &   getString() const { return str_value_; }

private:
  boost::posix_time::ptime    value_;
  LogMessage::String          str_value_;
};

} // namespace anl parser

#endif  // ANL_LOG_MESSAGE_HPP_INCLUDED


