#ifndef ANL_PARSER_HPP_INCLUDED
#define ANL_PARSER_HPP_INCLUDED

#include "anl/parser/log_message.hpp"

namespace anl { namespace parser {

typedef std::string   FilePath;

class ParserBase
{
protected:
  inline ParserBase( void )   {}
  virtual ~ParserBase( void )   {} = 0;
  
public:
  virtual bool          open( FilePath const &  filepath ) = 0;
  virtual bool          close( void ) = 0;
  
  virtual ParserBase&   operator >>( LogMessage const &  msg ) = 0;
  virtual bool          eof( void ) const = 0;
  
//-------------------------------------------------------//
// protected data
protected:
  
};


}} // namespace anl parser


#endif  // ANL_PARSER_HPP_INCLUDED

