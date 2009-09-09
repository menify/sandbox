#ifndef ANL_PARSER_HPP_INCLUDED
#define ANL_PARSER_HPP_INCLUDED

#include <ifstream>

#include "anl/parser/parser.hpp"

namespace anl { namespace parser
{

class KTraceParser: public ParserBase
{
public:
  KTraceParser( void );
  virtual ~KTraceParser( void )   { this->close(); }
  
  virtual bool          open( FilePath const &  filepath );
  virtual void          close( void );
  
  virtual ParserBase&   operator >>( LogMessage&  msg );
  virtual bool          eof( void ) const;
  
private:
  std::ifstream     log_stream_;
  
};


}} // namespace anl parser


#endif  // ANL_PARSER_HPP_INCLUDED

