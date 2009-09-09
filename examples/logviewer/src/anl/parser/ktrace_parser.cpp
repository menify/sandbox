
#include <boost/regex.hpp>
#include <boost/lexical_cast.hpp>
#include "boost/date_time/posix_time/posix_time.hpp"

#include "anl/log_values.hpp"

#include "anl/parser/ktrace_parser.hpp"


namespace anl { namespace parser
{

//===========================================================================//

KTraceParser::KTraceParser( void )
: log_parser_()
{
  this->log_parser_.exceptions( std::ifstream::goodbit );   // no exceptions with file operations
}

//===========================================================================//

bool    KTraceParser::open( FilePath const &  filepath )
{
  if (this->log_parser_.is_open())
  {
    this->log_parser_.close();
  }
  
  this->log_parser_.open( filepath );
  if (!this->log_parser_)
  {
    return false;
  }
  
  return true;
}

//===========================================================================//

void  KTraceParser::close( void )
{
  try
  {
    this->log_parser_.close();
  }
  catch (...)     // release resources shoold be always success
  {}
}

//===========================================================================//

ParserBase&   KTraceParser::operator >>( LogMessage&  msg )
{
  LogMessage  new_msg;
  
  new_msg["time"] = AttributeValueTime( boos::posix_time::second_clock::local_time() );
  new_msg["Thread"] = AttributeValueHexInt( 0x12345 );
  new_msg["Severity"] = AttributeValueString( "Error" );
  new_msg["Module"] = AttributeValueString( "Helper" );
  new_msg["Body"] = AttributeValueString( "This is a test message" );
  
  msg = new_msg;
  
  return *this;
}

}}  // namespace anl parser
