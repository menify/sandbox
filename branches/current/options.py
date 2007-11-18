
import os
import sys
import types
import string
import thread
import threading

import logging
import version

_Error = logging.Error
_Version = version.Version

#//---------------------------------------------------------------------------//

def     _is_option( option ):
    return isinstance( option, OptionBase )

#//---------------------------------------------------------------------------//

def     _is_options( option ):
    return isinstance( option, Options )

#//---------------------------------------------------------------------------//

def     _is_dict_option( option ):
    return isinstance( option, Options ) or type(option) is types.DictType

#//---------------------------------------------------------------------------//

def     _is_list( value ):
    return (type(value) is types.ListType) or (type(value) is types.TupleType)

#//---------------------------------------------------------------------------//

def     _is_dict( value ):
    return type(value) is types.DictType

#//---------------------------------------------------------------------------//

def     _is_string( value ):
    return type(value) is types.StringType

#//---------------------------------------------------------------------------//

def     _env_key( key ):
    return 'MPC_O_' + key.upper()

#//---------------------------------------------------------------------------//

def     EnvOptions( env ):
    
    options = env['MPC_OPTIONS']
    overridden_options = None
    
    options.Lock()      # lock the changing of the environment
    
    try:
        for k in options.iterkeys():
            
            env_key = _env_key( k )
            env_value = env.get( env_key )
            
            if env_value is None:
                continue
            
            if overridden_options is None:
                overridden_options = options.Clone()
            
            overridden_options[ k ] = env_value
            env[ env_key ] = None
        
        if overridden_options is not None:
            env['MPC_OPTIONS'] = overridden_options
            return overridden_options
    
    finally:
        options.Unlock()
    
    return options

#//===========================================================================//
#//===========================================================================//

class Options:
    
    def     __init__( self ):
        
        self.__dict__['__names_dict']         = {}
        self.__dict__['__ids_dict']           = {}
        self.__dict__['__helper_seq_num']     = 0
        self.__dict__['__lock']               = threading.Lock()
    
    #//-------------------------------------------------------//
    
    def     __add_to_dict( self, name, option ):
        self.__dict__['__names_dict'][ name ] = option
        
        opt_id = id( option )
        ids_dict = self.__dict__['__ids_dict']
        id_list = ids_dict.get( opt_id )
        
        if id_list is None:
            ids_dict[ opt_id ] = [ option, name ]
        else:
            id_list.append( name )
    
    #//-------------------------------------------------------//
    
    def     __find_option( self, name ):
        return self.__dict__['__names_dict'].get( name )
    
    #//-------------------------------------------------------//
    
    def     __add_option( self, name, value ):
        
        if not _is_option( value ):
            _Error( "Option '%s' is unknown and value '%s' is not an option" % (name,value) )
        
        self.__add_to_dict( name, value )
        
        value.SetOptions( self )
    
    #//-------------------------------------------------------//
    
    def     __set_option( self, name, value, update = 0 ):
        
        option = self.__find_option( name )
        
        if option is None:
            if not update:
                self.__add_option( name, value )
        else:
            
            if option is value:
                return
            
            if update and option.is_list:
                option.Append( value )
            else:
                option.Set( value )
    
    #//-------------------------------------------------------//
    
    def     __get_option( self, name, attribute = 0):
        option = self.__find_option( name )
        
        if option is None:
            if attribute:   raise AttributeError( "Unknown option: '%s'" % (name) )
            else:           raise KeyError( "Unknown option: '%s'" % (name) )
        
        return option
    
    #//-------------------------------------------------------//
    
    def     __list_options( self ):
        return self.__dict__['__names_dict'].iterkeys()
    
    #//-------------------------------------------------------//
    
    def     __setattr__(self, name, value):
        self.__set_option( name, value )
    
    #//-------------------------------------------------------//
    
    def     __getattr__( self, name ):
        return self.__get_option( name, attribute = 1 )
    
    #//-------------------------------------------------------//
    
    def     __setitem__( self, name, value ):
        self.__set_option( name, value )
        
    #//-------------------------------------------------------//
    
    def     __getitem__( self, name ):
        return self.__get_option( name )
    
    #//-------------------------------------------------------//
    
    def     keys( self ):
        return self.__dict__['__names_dict'].keys()
    
    def     iterkeys( self ):
        return self.__dict__['__names_dict'].iterkeys()
    
    #//-------------------------------------------------------//
    
    def     has_key( self, key ):
        if self.__find_option( key ):
            return 1
        
        return 0
    
    #//-------------------------------------------------------//
    
    def     get( self, key, default = None ):
        value = self.__find_option( key )
        if value is None:
            return default
        
        return value
    
    #//-------------------------------------------------------//
    
    def     update( self, args ):
        
        if args:
            for key, value in args.iteritems():
                self.__set_option( key, value, update = 1 )
    
    #//-------------------------------------------------------//
    
    def     __iadd__(self, other ):
        
        self.update( other )
        
        return self
    
    #//-------------------------------------------------------//
    
    def     OptionNames( self, opt ):
        
        names = self.__dict__['__ids_dict'].get( id(opt), [ None ] )
        return names[1:]
    
    #//-------------------------------------------------------//
    
    def     Clone( self ):
        
        options = Options()
        
        for ident, id_list     in    self.__dict__['__ids_dict'].iteritems():
            
            opt = id_list[0].Clone( options )
            names = id_list[1:]
            
            for name in names:
                options[ name ] = opt
        
        return options
    
    #//-------------------------------------------------------//
    
    def     __nonzero__( self ):
        return len( self.__dict__['__names_dict'] )
    
    #//-------------------------------------------------------//
    
    def     If( self ):
        return _ConditionalOptions( self );
    
    #//-------------------------------------------------------//
    
    def     __repr__( self ):
        return "<MPC options>"
    
    def     __str__( self ):
        return str( self.__dict__['__names_dict'] )
    
    #//-------------------------------------------------------//
    
    def     __linker_name( self ):
        
        self.__dict__['__helper_seq_num'] += 1
        
        return '__linker_' + str(id( self )) + '_' + str( self.__dict__['__helper_seq_num'] )
    
    #//-------------------------------------------------------//
    
    def     LinkToEnv( self, env ):
        
        linker = IntOption( 0 )
        linker_name = self.__linker_name()
        
        condition = lambda options, name = linker_name : options[ name ] != 0
        
        for ident, id_list   in   self.__dict__['__ids_dict'].iteritems():
            opt = id_list[0]
            opt.AppendPreCondition( condition )
        
        self[ linker_name ] = linker
        env[ _env_key( linker_name ) ] = 1
        
    #//-------------------------------------------------------//
    
    def     UnlinkToEnv( self ):
        for ident, id_list  in  self.__dict__['__ids_dict'].iteritems():
            opt = id_list[0]
            opt.UndoPreCondition()
    
    #//-------------------------------------------------------//
    
    def     LinkToKW( self, **kw ):
        
        env = {}
        self.LinkToEnv( env )
        
        self.update( kw )
        
        self.UnlinkToEnv()
        
        return env
    
    #//-------------------------------------------------------//
    
    def     Lock( self ):       self.__dict__['__lock'].acquire()
    def     Unlock( self ):     self.__dict__['__lock'].release()

#//===========================================================================//
#//===========================================================================//

def     _append_values( values_list, values, unique ):
    if unique:
        for v in values:
            if not v in values_list:
                values_list.append( v )
    else:
        values_list += values

#//---------------------------------------------------------------------------//

def     _remove_values( values_list, values ):
    for v in values:
        while 1:
            try:
                values_list.remove( v )
            except ValueError:
                break

#//---------------------------------------------------------------------------//

def     _split_value( value, separator ):
    
    if _is_string( value ):
        
        if value:
            if separator:
                value = value.split( separator )
            else:
                value = [ value ]
        else:
            value = []
    
    return value

#//---------------------------------------------------------------------------//

def     _add_raw_value( self_values, option, value ):
    
    cv = option._convert_value( value )
    
    if not _is_list( cv ):
        cv = [ cv ]
    
    for v in cv:
        self_values.append( ('v', v) )

#//---------------------------------------------------------------------------//

def     _add_option( self_values, option, value ):
    
    name = value.Names()[0]
    
    self_values.append( ('n', name) )
    
    if __debug__:
        option._convert_value( value.Get() )      # check the current value

#//---------------------------------------------------------------------------//

def     _convert_value_to_list( values, option ):
    
    if values is None:
        if not option.is_list:
            _Error( "Can't convert 'None' value" )
        
        values = []
    
    else:
        if option.is_list:
            values = _split_value( values, option.separator )
        
        if not _is_list( values ):
            values = [ values ]
    
    return values


#//===========================================================================//
#//===========================================================================//

class   _ConditionalValue:
    
    def     __init__( self, value, option ):
        
        if isinstance( value, _ConditionalValue ):
            self.values = value.values
            return
        
        values = _convert_value_to_list( value, option )
        
        self_values = []
        
        for v in values:
            if _is_option( v ):
                _add_option( self_values, option, v )
            
            else:
                if v is None:
                    _Error("Can't convert 'None' value" )
                
                _add_raw_value( self_values, option, v )
        
        self.values = self_values
    
    #//-------------------------------------------------------//
    
    def     GetList( self, option ):
        
        values = []
        
        convert_value = option._convert_value
        
        for v in self.values:
            if v[0] == 'v':
                values.append( v[1] )
            else:
                opt_value = option.options[ v[1] ].Get()
                
                cv = convert_value( opt_value )
                
                if _is_list( cv ):
                    values += cv
                else:
                    values.append( cv )
        
        return values
    
    #//-------------------------------------------------------//
    
    def     Get( self, option ):
        values = self.GetList( option )
        
        if option.is_list:
            return values
        
        if len(values) != 1:
            _Error("Can't convert list of values to non-list option" )
        
        return values[0]

#//===========================================================================//
#//===========================================================================//

class   _Condition:
    
    def     __init__( self, name, cond_id, value ):
        self.name = name
        self.cond_id = cond_id
        self.value =  value
    
    #//-------------------------------------------------------//
    
    def     __call__( self, options ):
        
        option = options[ self.name ]
        
        return getattr( option, self.cond_id )( self.value )

#//===========================================================================//
#//===========================================================================//

class   _ConditionsList:
    
    def    __init__( self ):
        self.conditions = []
        self.value = None
        self.operation = None
    
    #//-------------------------------------------------------//
    
    def     Append( self, cond ):
        
        if isinstance( cond, _ConditionsList ):
            self.conditions += cond.conditions
        
        else:
            if __debug__:
                if not callable( cond ):
                    _Error( "Condition should be callable object: condition( options )" )
            
            self.conditions.append( cond )
    
    #//-------------------------------------------------------//
    
    def     __delitem__( self, index ):
        
        try:
            del self.conditions[ index ]
        except IndexError:
            pass
    
    #//-------------------------------------------------------//
    
    def     SetValue( self, value, operation ):
        
        self.value = value
        self.operation = operation
    
    #//-------------------------------------------------------//
    
    def     GetValue( self ):
        return (self.operation, self.value )
    
    #//-------------------------------------------------------//
    
    def     IsTrue( self, options ):
        for c in self.conditions:
            if not c( options ):
                return 0
        
        return 1
    
    #//-------------------------------------------------------//
    
    def     Clone( self ):
        clone = _ConditionsList()
        clone.conditions = self.conditions[:]
        clone.value = self.value
        clone.operation = self.operation
        
        return clone

#//===========================================================================//
#//===========================================================================//

class       _NoOptions:
    
    def     __error( self ):    _Error("The option is not linked with any instance of options.")
    def     __setattr__(self, name, value):     self.__error()
    def     __setitem__( self, name, value ):   self.__error()
    def     __getattr__( self, name ):          self.__error()
    def     __getitem__(self, name ):           self.__error()


#//===========================================================================//
#//===========================================================================//

class   OptionBase:
    
    def     _init_base( self, help, default, is_list, separator, unique, options = None ):
        
        if options is None:
            options = _NoOptions()
        
        self.options = options
        self.help = help
        self.conditions = []
        self.preconditions_list = _ConditionsList()
        self.is_list = is_list
        self.separator = separator
        self.unique = unique
        self.changed = 0
        
        if __debug__:
            self.active_threads = []
        
        self.SetDefault( default )
    
    #//-------------------------------------------------------//
    
    def     _clone_base( self, clone, options ):
        
        self.options = options
        self.help = clone.help
        
        self._copy_conditions( clone )
        
        self.is_list = clone.is_list
        self.separator = clone.separator
        self.unique = clone.unique
        
        if __debug__:
            self.active_threads = []
        
        self.default = clone.default
        self.default_value = clone.default_value
    
    #//-------------------------------------------------------//
    
    def     _copy_conditions( self, clone ):
        self.conditions = clone.conditions[:]
        self.preconditions_list = _ConditionsList()
    
    #//-------------------------------------------------------//
    
    def     SetOptions( self, options ):
        
        if not _is_options( self.options ):
            self.options = options
       
        elif self.options is not options:
            _Error("The option is already linked with another options.")
    
    #//-------------------------------------------------------//
    
    def     Names( self ):
        
        names = self.options.OptionNames( self )
        
        if __debug__:
            if not names:
                _Error( "No names of the option" )
        
        return names
    
    #//-------------------------------------------------------//
    
    def     Convert( self, value ):         return _ConditionalValue( value, self ).Get( self )
    
    #//-------------------------------------------------------//
    
    def     __conditions_values( self, values ):
        
        unique = self.unique
        options = self.options
        
        for c in self.conditions:
            if c.IsTrue( options ):
                
                op, v = c.GetValue()
                v = v.Get( self )
                
                if op == '=':
                    values = v
                
                elif op == '+':
                    _append_values( values, v, unique )
                
                elif op == '-':
                    _remove_values( values, v )
        
        return values
    
    #//-------------------------------------------------------//
    
    def    Get( self ):
        
        if __debug__:
            thread_id = thread.get_ident()
            if self.active_threads.count( thread_id ):
                _Error("Recursive evaluation of the option")
            self.active_threads.append( thread_id )
        
        values = self.default_value
        if self.is_list:
            values = values[:]
        
        values = self.__conditions_values( values )
        
        if __debug__:
            self.active_threads.remove( thread_id )
        
        return values
    
    #//-------------------------------------------------------//
    
    def     AppendPreCondition( self, condition ):
        self.preconditions_list.Append( condition )
    
    #//-------------------------------------------------------//
    
    def     UndoPreCondition( self ):
        del self.preconditions_list[ -1 ]
    
    #//-------------------------------------------------------//
    
    def     Undo( self ):
        del self.conditions[ -1 ]
    
    #//-------------------------------------------------------//
    
    def     Set( self, value ):
        self.SetIf( lambda options: 1, value )
    
    #//-------------------------------------------------------//
    
    def     Append( self, value ):
        self.AppendIf( lambda options: 1, value )
    
    #//-------------------------------------------------------//
    
    def     Remove( self, value ):
        self.RemoveIf( lambda options: 1, value )
    
    #//-------------------------------------------------------//
    
    def     __iadd__(self, value ):
        self.Append( value )
        return self
    
    #//-------------------------------------------------------//
    
    def     __isub__(self, value ):
        self.Remove( value )
        return self
    
    #//-------------------------------------------------------//
    
    def     SetIf( self, condition, value ):
        self._add_condition( condition, value, '=')
    
    #//-------------------------------------------------------//
    
    def     AppendIf( self, condition, value ):
        self._add_condition( condition, value, '+')
    
    #//-------------------------------------------------------//
    
    def     RemoveIf( self, condition, value ):
        self._add_condition( condition, value, '-' )
    
    #//-------------------------------------------------------//
    
    def     _add_condition( self, condition, value, operation ):
        
        if __debug__:
            if (not self.is_list) and (operation != '='):
                _Error( "Append/remove operations are not allowed for none-list options." )
        
        value = _ConditionalValue( value, self )
        
        conditions_list = _ConditionsList()
        
        conditions_list.Append( self.preconditions_list )
        conditions_list.Append( condition )
        
        conditions_list.SetValue( value, operation )
        
        self.conditions.append( conditions_list )
        
        self.changed = 1
        
        if __debug__:
            self.Get()   # check for recursion of conditions
    
    #//-------------------------------------------------------//
    
    def     SetDefault( self, default ):
        self.default = default
        self.default_value = self.Convert( default )
    
    #//-------------------------------------------------------//
    
    def     __lt__( self, other):       return self.Get() <  self.Convert( other )
    def     _lt( self, other):          return self.Get() <  other.Get( self )
    def     __le__( self, other):       return self.Get() <= self.Convert( other )
    def     _le( self, other):          return self.Get() <= other.Get( self )
    def     __eq__( self, other):       return self.Get() == self.Convert( other )
    def     _eq( self, other):          return self.Get() == other.Get( self )
    def     __ne__( self, other):       return self.Get() != self.Convert( other )
    def     _ne( self, other):          return self.Get() != other.Get( self )
    def     __gt__( self, other):       return self.Get() >  self.Convert( other )
    def     _gt( self, other):          return self.Get() >  other.Get( self )
    def     __ge__( self, other):       return self.Get() >= self.Convert( other )
    def     _ge( self, other):          return self.Get() >= other.Get( self )
    
    #//-------------------------------------------------------//
    
    def     __contains__(self, other):
        return self.has( other )
    
    def     has( self, other ):
        return self._has( _ConditionalValue( other, self ) )
    
    def     _has( self, other ):
        
        if __debug__:
            if not self.is_list:
                _Error("Must be a list option")
        
        values = self.Get()
        
        for v in other.Get( self ):
            if v not in values:
                return 0
        
        return 1
    
    #//-------------------------------------------------------//
    
    def     has_any( self, other ):
        return self._has_any( _ConditionalValue( other, self ) )
    
    def     _has_any( self, other ):
        
        if __debug__:
            if not self.is_list:
                _Error("Must be a list option")
        
        values = self.Get()
        
        for v in other.Get( self ):
            if v in values:
                return 1
        
        return 0
    
    #//-------------------------------------------------------//
    
    def     one_of( self, values ):
        return self._one_of( _ConditionalValue( values, self ) )
    
    def     _one_of( self, values ):
        
        if __debug__:
            if self.is_list:
                _Error("Must be a non-list option")
        
        return self.Get() in values.GetList( self )
    
    #//-------------------------------------------------------//
    
    def     Clone( self, options ):
        clone = OptionBase()
        
        clone.__dict__ = self.__dict__.copy();
        clone.__class__ = self.__class__;
        
        clone._clone_base( self, options )
        
        return clone
    
    #//-------------------------------------------------------//
    
    def     __value_str( self, value ):
        if _is_list( value ):
            sep = self.separator[:]
            return sep.join( value )
        
        return str( value )
    
    #//-------------------------------------------------------//
    
    def     __nonzero__( self ):
        if self.Get(): return 1
        return 0
    
    #//-------------------------------------------------------//
    
    def     __str__( self ):
        return self.__value_str( self.Get() )
    
    #//-------------------------------------------------------//
    
    def     ResetChanged( self ):   self.changed = 0
    def     IsChanged( self ):      return self.changed
    
    #//-------------------------------------------------------//
    
    def     Default( self ):
        return self.__value_str( self.default_value )

#//===========================================================================//
#//===========================================================================//

class   BoolOption (OptionBase):
    
    __true_strings  = ( 'y', 'yes', 'true', 't', '1', 'on', 'enabled' )
    __false_strings = ( 'n', 'no', 'false', 'f', '0', 'off', 'disabled' )
    
    __invert_bool = {
               'y': 'no',
               'yes': 'no',
               't': 'false',
               '1': 'false',
               'true': 'false',
               'on': 'off',
               
               'n': 'yes',
               'no': 'yes',
               'f': 'true',
               '0': 'true',
               'false': 'true',
               'off': 'on',
               'disabled' : 'enabled',
               'enabled' : 'disabled'
             }
    
    #//-------------------------------------------------------//
    def     __init__( self, default = 0, is_list = 0, separator = ' ', unique = 1, help = None ):
        self._init_base( help, default, is_list, separator, unique )
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val ):
        
        lval = str( val ).lower()
        if lval in self.__true_strings: return 1
        if lval in self.__false_strings: return 0
        
        _Error( "Invalid boolean value: '%s'" % (val) )
    
    #//-------------------------------------------------------//
    
    def     __str__( self ):
        
        value_str = self.__invert_bool[ str( self.default ).lower() ]
        
        if self == self.default:
            value_str = self.__invert_bool[ value_str ]
        
        return value_str
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'yes/no, true/false, on/off, enabled/disabled, 1/0'
    
    #//-------------------------------------------------------//
    
    def     Default( self ):
        return self.__invert_bool[ self.__invert_bool[ str( self.default ) ] ]
 
#//===========================================================================//
#//===========================================================================//

class   EnumOption (OptionBase):
    
    def     __init__( self, default, allowed_values = None, aliases = None, is_list = 0, separator = ' ', unique = 1, help = None, options = None):
        
        self.allowed_values = []
        self.aliases = {}
        
        self.AddValues( allowed_values )
        
        self._init_base( help, default, is_list, separator, unique, options )
        
        self.AddAliases( aliases )
        
    #//-------------------------------------------------------//
    
    def     __map_values( self, values ):
        
        if _is_list( values ):
            
            mapped_val = []
            
            for v in values:
                v = self.__map_values( v )
                
                if _is_list( v ):
                    mapped_val += v
                else:
                    mapped_val.append( v )
            
            return mapped_val
        
        #//-------------------------------------------------------//
        
        val = str(values).lower()
        val = self.aliases.get( val, val )
        
        if _is_list( val ):
            
            mapped_val = []
            
            for v in val:
                v = self.__map_values( v )
                if v is None:
                    return None
               
                if _is_list( v ):
                    mapped_val += v
                else:
                    mapped_val.append( v )
            
            return mapped_val
        
        if not val in self.allowed_values:
            return None
        
        return val
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val ):
        
        value = self.__map_values( val )
        
        if value is None:
            _Error( "Invalid value '%s'" % (val) )
        
        return value
    
    #//=======================================================//
    
    def     AddValues( self, values ):
        if not values:
            return
        
        elif not _is_list( values ):
            values = [ values ]
        
        allowed_values = self.allowed_values
        
        for v in values:
            if self.__map_values( v ) is None:
                allowed_values.append( v )
    
    #//=======================================================//
    
    def     AddAliases( self, aliases, values = None ):
        
        if not aliases:
            return
        
        if _is_dict( aliases ):
            
            for k,v  in  aliases.iteritems():
                self.AddAliases( aliases = k, values = v )
            return
        
        if not values:
            return
        
        mapped_values = self.__map_values( values )
        
        if __debug__:
            if mapped_values is None:
                _Error( "Invalid value(s): %s" % (values) )
        
        values = mapped_values
        
        #//-------------------------------------------------------//
        
        if (not self.is_list) and (_is_list( values ) and (len(values) > 1)):
            _Error( "Can not set multiple values: %s to none-list option" % (aliases) )
        
        #//-------------------------------------------------------//
        
        if not _is_list( aliases ):
            aliases = [ aliases ]
        
        for a in aliases:
            if self.__map_values( a ) is None:
                self.aliases[ str(a).lower() ] = values
    
    #//=======================================================//
    
    def     AllowedValues( self ):
        return self.allowed_values
    
    #//=======================================================//
    
    def     Aliases( self ):
        return self.aliases
    
    #//=======================================================//
    
    def     __find_aliases( self, value ):
        
        mapped_values = []
        aliases = self.aliases
        
        for k,v in aliases.iteritems():
            if v == value:
                mapped_values.append( k )
        
        return mapped_values
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        
        allowed_values = []
        for v in self.allowed_values:
            
            mv = self.__find_aliases( v )
            if len( mv ) > 0:
                v = v + '(or ' + string.join( mv, ' or ') + ')'
            
            allowed_values.append( v )
        
        return string.join( allowed_values, ', ')
    
    #//=======================================================//
    
    def     Clone( self, options ):
        
        clone = EnumOption( default = self.default,
                            allowed_values = self.allowed_values,
                            aliases = self.aliases,
                            is_list = self.is_list,
                            separator = self.separator,
                            unique = self.unique,
                            help = self.help,
                            options = options )
        
        clone._copy_conditions( self )
        
        return clone



#//===========================================================================//
#//===========================================================================//

class   IntOption (OptionBase):
    
    def     __init__( self, default, min = -(sys.maxint - 1), max = sys.maxint, is_list = 0, separator = ' ', unique = 1, help = None ):
        
        self.min_value = int( min )
        self.max_value = int( max )
        
        if __debug__:
            if self.min_value > self.max_value:
                _Error( "Minimal value: %d is greater than maximal value: %d " % (min, max) )
        
        self._init_base( help, default, is_list, separator, unique )
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val ):
        
        int_val = int(val)
        if (int_val < self.min_value) or (int_val > self.max_value):
            _Error( "Invalid value: %s" % (val) )
        
        return int_val
    
    #//-------------------------------------------------------//
    
    def     __int__( self ):
        return self.Get()
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'from %d to %d' % (self.min_value, self.max_value)

#//===========================================================================//
#//===========================================================================//

class   StrOption (OptionBase):
    
    def     __init__( self, default = None, is_list = 0, separator = ' ', unique = 1, ignore_case = 0, help = None ):
        
        if default is None:
            default = ''
        
        self.ignore_case = ignore_case
        self._init_base( help, default, is_list, separator, unique )
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, value ):
        
        value = str(value)
        if self.ignore_case:
            value = value.lower()
        
        return value
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'any strings'

#//===========================================================================//
#//===========================================================================//

class   LinkedOption (OptionBase):
    
    def     __init__( self, default, options, linked_opt_name, is_list = 0, separator = ' ', unique = 1, help = None ):
        
        self.linked_opt_name = linked_opt_name
        
        self._init_base( help, default, is_list, separator, unique, options )
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, value ):
        
        linked_option = self.options[ self.linked_opt_name ]
        
        return linked_option._convert_value( value )
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        linked_option = self.options[ self.linked_opt_name ]
        return linked_option.AllowedValuesStr()
        

#//===========================================================================//
#//===========================================================================//

class   VersionOption (OptionBase):
    
    def     __init__( self, default = None, is_list = 0, separator = ' ', unique = 1, help = None ):
        
        if default is None:
            default = ''
        
        self._init_base( help, default, is_list, separator, unique )
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val ):
        
        return _Version( val )
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'Version in format N[a].N[a].N[a]... (where N - dec numbers, a - alphas)'

#//===========================================================================//
#//===========================================================================//

class   PathOption (OptionBase):
    
    def     __init__( self, default = None, is_list = 0, separator = None, unique = 1, help = None ):
        
        if default is None:
            default = ''
        
        if (separator is None):
            separator = os.pathsep
        
        self._init_base( help, default, is_list, separator, unique )
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val ):
        
        path = os.path.normcase( os.path.normpath( val ) )
        
        return path
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'Paths'

#//===========================================================================//
#//===========================================================================//

class _ConditionalOptions:
    
    def     __init__( self, options, conditions_list = None ):
        
        self.__dict__['__options'] = options
        
        if conditions_list is not None:
            self.__dict__['__conditions_list'] = conditions_list.Clone()
        else:
            self.__dict__['__conditions_list'] = _ConditionsList()
    
    #//-------------------------------------------------------//
    
    def     __setattr__(self, name, value):
        
        options = self.__dict__['__options']
        option = options.get( name )
        
        if option is None:
            if _is_option( value ):
                _Error( "Can't add new option '%s' within condition." % (name) )
            else:
                _Error( "Unknown option: %s" % (name) )
        
        if option is value:
            return
        
        option.SetIf( self.__dict__['__conditions_list'], value )
    
    #//-------------------------------------------------------//
    
    def     __setitem__( self, name, value ):
        self.__setattr__( name, value )
    
    #//-------------------------------------------------------//
    
    def     __getattr__( self, name ):
        
        options = self.__dict__['__options']
        option = options.get( name )
        
        if option is None:
            _Error( "Unknown option: %s" % (name) )
        
        return _ConditionalOption( name, option, options, self.__dict__['__conditions_list'] )
    
    #//-------------------------------------------------------//
    
    def     __getitem__(self, name ):
        return self.__getattr__( name )
    
    #//-------------------------------------------------------//
    
    def     __repr__( self ):
        return "<_Conditional Options>"

#//===========================================================================//
#//===========================================================================//

class   _ConditionalOption:
    
    def     __init__( self, name, option, options, conditions_list ):
        
        self.name = name
        self.option = option
        self.options = options
        self.conditions_list = conditions_list
    
    #//-------------------------------------------------------//
    
    def     __add_condition( self, value, operation, condition = None ):
        
        conditions_list = self.conditions_list
        
        if condition is not None:
            conditions_list = conditions_list.Clone()
            conditions_list.Append( condition )
        
        self.option._add_condition( conditions_list, value, operation )
    
    #//-------------------------------------------------------//
    
    def     Set( self, value ):                     self.__add_condition( value, '=' )
    def     SetIf( self, condition, value ):        self.__add_condition( value, '=', condition )
    def     Append( self, value ):                  self.__add_condition( value, '+' )
    def     AppendIf( self, condition, value ):     self.__add_condition( value, '+', condition )
    def     Remove( self, value ):                  self.__add_condition( value, '-' )
    def     RemoveIf( self, condition, value ):     self.__add_condition( value, '-', condition )
    
    #//-------------------------------------------------------//
    
    def     __iadd__( self, value ):
        self.Append( value )
        return self.option
    
    #//-------------------------------------------------------//
    
    def     __isub__( self, value ):
        self.Remove( value )
        return self.option
    
    #//-------------------------------------------------------//
    
    def     __getitem__( self, value ):
        
        if self.option.is_list:
            return self.has( value )
        
        return self.eq( value )
    
    #//-------------------------------------------------------//
    
    def     __cond_options( self, cond_id, value ):
        
        conditions_list = self.conditions_list.Clone()
        
        value = _ConditionalValue( value, self.option )
        conditions_list.Append( _Condition( self.name, cond_id, value ) )
        
        return _ConditionalOptions( self.options, conditions_list )
    
    #//-------------------------------------------------------//
    
    def     has( self, value ):         return self.__cond_options( '_has', value )
    def     has_any( self, values ):    return self.__cond_options( '_has_any', values )
    def     one_of( self, values ):     return self.__cond_options( '_one_of', values )
    def     eq( self, value ):          return self.__cond_options( '_eq', value )
    def     ne( self, value ):          return self.__cond_options( '_ne', value )
    def     gt( self, value ):          return self.__cond_options( '_gt', value )
    def     ge( self, value ):          return self.__cond_options( '_ge', value )
    def     lt( self, value ):          return self.__cond_options( '_lt', value )
    def     le( self, value ):          return self.__cond_options( '_le', value )
