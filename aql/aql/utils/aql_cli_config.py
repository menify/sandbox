#
# Copyright (c) 2012 The developers of Aqualid project - http://aqualid.googlecode.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import optparse

__all__ = ( 'CLIOption', 'CLIConfig' )

#//===========================================================================//

class   CLIOption( object ):
  __slots__ = (
    'cli_name', 'cli_long_name', 'opt_name', 'value_type', 'default', 'help', 'metavar'
  )
  
  def   __init__( self, cli_name, cli_long_name, opt_name, value_type, default, help, metavar = None ):
    self.cli_name = cli_name
    self.cli_long_name = cli_long_name
    self.opt_name = opt_name
    self.value_type = value_type
    self.default = value_type(default)
    self.help = help
    self.metavar = metavar
  
  #//-------------------------------------------------------//
  
  def   addToParser( self, parser ):
    args = (self.cli_name, self.cli_long_name)
    
    if self.value_type is bool:
      action = 'store_false' if self.default else 'store_true'
    else:
      action = 'store'
    
    kw = { 'dest': self.opt_name, 'help': self.help, 'action': action }
    if self.metavar:
      kw['metavar'] = self.metavar
    parser.add_option( *args, **kw )

#//===========================================================================//

class   CLIConfig( object ):
  
  #//-------------------------------------------------------//
  
  def   __init__( self, cli_usage, cli_options, args ):
    
    super(CLIConfig, self).__setattr__( 'values', {} )
    super(CLIConfig, self).__setattr__( 'targets', [] )
    super(CLIConfig, self).__setattr__( '_set_options', set() )
    super(CLIConfig, self).__setattr__( '_defaults', {} )
    
    self.__parseArguments( cli_usage, cli_options, args )
    
  #//-------------------------------------------------------//
  
  @staticmethod
  def   __getArgsParser( cli_usage, cli_options ):
    parser = optparse.OptionParser( usage = cli_usage )
    
    for opt in cli_options:
      opt.addToParser( parser )
    return parser
  
  #//-------------------------------------------------------//
  
  @staticmethod
  def   __getDefaults( cli_options ):
    defaults = {}
    
    for opt in cli_options:
      defaults[ opt.opt_name ] = (opt.default, opt.value_type)
    
    return defaults
  
  #//-------------------------------------------------------//
  
  def   __parseValues( self, args ):
    values = self.values
    targets = self.targets
    
    for arg in args:
      name, sep, value = arg.partition('=')
      name = name.strip()
      if sep:
        values[name] = value.strip()
      else:
        targets.append( name )
  
  #//-------------------------------------------------------//
  
  def   __parseOptions( self, cli_options, args ):
    defaults = self.__getDefaults( cli_options )
    self._defaults = defaults
    
    for opt in cli_options:
      name = opt.opt_name
      value = getattr( args, name )
      if value is None:
        value = defaults[ name ][0]
      else:
        self._set_options.add( name )
      
      super(CLIConfig, self).__setattr__( name, value )
  
  #//-------------------------------------------------------//
  
  def   __parseArguments( self, cli_usage, cli_options, cli_args ):
    parser = self.__getArgsParser( cli_usage, cli_options )
    args, values = parser.parse_args( cli_args )
    
    self.__parseValues( values )
    self.__parseOptions( cli_options, args )
  
  #//-------------------------------------------------------//
  
  def   include( self, config_file ):
    locals = {}
    defaults = self._defaults
    set_options = self._set_options
    
    execFile( config_file, locals )
    for name, value in locals.items():
      if name in defaults:
        self.setDefault( name, value )
  
  #//-------------------------------------------------------//
  
  def   __set( self, name, value ):
    defaults = self._defaults
    
    try:
      value_type = defaults[ name ][1]
    except KeyError:
      defaults[ name ] = (value, type(value))
    else:
      value = value_type( value )
    
    super(CLIConfig, self).__setattr__( name, value )
  
  #//-------------------------------------------------------//
  
  def   setDefault( self, name, value ):
    if name not in self._set_options:
      self.__set( name, value )
  
  #//-------------------------------------------------------//
  
  def   __setattr__( self, name, value ):
    self.__set( name, value )
    self._set_options.add( name )