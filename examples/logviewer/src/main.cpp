#include <stddef.h>
#include <cstdlib>
#include <string>
#include <iostream>
#include <fstream>

#include "tools/tracer.hpp"

static void   usage( std::string const &  exe_name )
{
  std::cout << "Analyzer of Neo Logs." << std::endl
            << "Usage: " << std::endl
            << exe_name << " <path to trace output>" << std::endl;
}

//===========================================================================//

int main(int  argc, char*  argv[])
{
  if(argc < 2)
  {
    usage( std::string(argv[0]) );
    return EXIT_FAILURE;
  }
  
  char const * const    log_filename = argv[1];
  
  TraceInfo traceFileInfo;
  if(!ReadTraceInfoFromFile(inputFilename, traceFileInfo))
  {
    return(1);
  }

  return EXIT_SUCCESS;
}
