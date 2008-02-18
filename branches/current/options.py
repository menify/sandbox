
import os
import sys
import types
import thread

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

def     _is_sequence( value ):
    t = type(value)
    return (t is types.ListType) or (t is types.TupleType)

def     _to_list( value ):
    
    if not _is_sequence(value):
        if value is None:
            return ()
        
        return ( value, )
    
    return value

#//---------------------------------------------------------------------------//

def     _is_dict( value ):
    return type(value) is types.DictType

#//---------------------------------------------------------------------------//

def     _is_string( value ):
    return type(value) is types.StringType

#//---------------------------------------------------------------------------//

def     EnvOptions( env ):
    
    options = env['AQL_OPTIONS']
    options.SetEnv( env )
    
    return options


#//===========================================================================//
#//===========================================================================//

class Options:
    
    def     __init__( self ):
        
        self.__dict__['__names_dict']       = {}
        self.__dict__['__ids_dict']         = {}
        self.__dict__['__env']              = None
    
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
            #~ if _is_sequence( value ):   is_list = 1
            #~ else:                       is_list = 0
            
            #~ value = StrOption( initial_value = value, is_list = is_list )   # use the default option type for unknown options
        
        self.__add_to_dict( name, value )
        
        value.SetOptions( self )
    
    #//-------------------------------------------------------//
    
    def     __set_option( self, name, value, update = 0, quiet = 0 ):
        
        option = self.__find_option( name )
        
        if option is None:
            if (not update) or (not quiet):
                self.__add_option( name, value )
        else:
            
            if option is value:
                return
            
            if update:
                option.Update( value )
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
    
    def     update( self, args, quiet = 1 ):
        
        if args:
            set_option = self.__set_option
            
            for key, value in args.iteritems():
                set_option( key, value, update = 1, quiet = quiet )
    
    #//-------------------------------------------------------//
    
    def     __iadd__(self, other ):
        
        self.update( other )
        
        return self
    
    #//-------------------------------------------------------//
    
    def     OptionNames( self, opt ):
        
        names = self.__dict__['__ids_dict'].get( id(opt), [ None ] )
        return names[1:]
    
    #//-------------------------------------------------------//
    
    def     __call__( self, **kw ):
        options = self.Clone()
        options.update( kw, quiet = 0 )
        
        return options
    
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
        return "<AQL options>"
    
    def     __str__( self ):
        return str( self.__dict__['__names_dict'] )
    
    #//-------------------------------------------------------//
    
    def     Env( self ):
        return self.__dict__['__env']
    
    def     SetEnv( self, env ):
        self.__dict__['__env'] = env

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
    
    cv = _to_list( option._convert_value( value ) )
    
    for v in cv:
        self_values.append( ('v', v) )

#//---------------------------------------------------------------------------//

def     _add_option( self_values, option, value ):
    
    name = value.Names()[0]
    
    self_values.append( ('n', name) )
    
    if __debug__:
        option.Convert( value.Get() )      # check the current value

#//---------------------------------------------------------------------------//

def     _convert_value_to_list( values, option ):
    
    if values is None:
        if not option.is_list:
            _Error( "Can't convert 'None' value" )
        
        values = []
    
    else:
        if option.is_list:
            values = _split_value( values, option.separator )
        
        values = _to_list( values )
    
    return values

def     _always_true( options ):    return 1

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
                
                values.extend( map( convert_value, _to_list( opt_value ) ) )
        
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

class       _NoneOptions:
    
    def     __error( self ):    _Error("The option is not linked with any instance of options.")
    def     __setattr__(self, name, value):     self.__error()
    def     __setitem__( self, name, value ):   self.__error()
    def     __getattr__( self, name ):          self.__error()
    def     __getitem__(self, name ):           self.__error()

_none_options = _NoneOptions()

#//===========================================================================//
#//===========================================================================//

class   OptionBase:
    
    def     _init_base( self, help, initial_value, is_list, separator, unique, update_set, options = None ):
        
        if options is None:
            options = _none_options
        
        self.options = options
        self.help = help
        self.conditions = []
        self.preconditions_list = _ConditionsList()
        self.is_list = is_list
        self.separator = separator
        self.unique = unique
        
        if update_set or (not is_list):
            self.Update = self.Set
        else:
            self.Update = self.Append
        
        if __debug__:
            self.active_threads = []
        
        if is_list:
            self.Append( initial_value )
        else:
            self.Set( initial_value )
    
    #//-------------------------------------------------------//
    
    def     _clone_base( self, clone, options ):
        
        self.options = options
        self.help = clone.help
        
        self._copy_conditions( clone )
        
        self.is_list = clone.is_list
        self.separator = clone.separator
        self.unique = clone.unique
        
        if clone.Update == clone.Set:
            self.Update = self.Set
        else:
            self.Update = self.Append
        
        if __debug__:
            self.active_threads = []
    
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
    
    def     __conditions_values( self ):
        
        values = []
        
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
        
        values = self.__conditions_values()
        
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
        self.SetIf( _always_true, value )
    
    #//-------------------------------------------------------//
    
    def     Preset( self, value ):
        self.PresetIf( _always_true, value )
    
    #//-------------------------------------------------------//
    
    def     Append( self, value ):
        self.AppendIf( _always_true, value )
    
    #//-------------------------------------------------------//
    
    def     Prepend( self, value ):
        self.PrependIf( _always_true, value )
    
    #//-------------------------------------------------------//
    
    def     Remove( self, value ):
        self.RemoveIf( _always_true, value )
    
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
    
    def     PresetIf( self, condition, value ):
        self._add_condition( condition, value, '=', pre = 1)
    
    #//-------------------------------------------------------//
    
    def     AppendIf( self, condition, value ):
        self._add_condition( condition, value, '+')
    
    #//-------------------------------------------------------//
    
    def     PrependIf( self, condition, value ):
        self._add_condition( condition, value, '+', pre = 1)
    
    #//-------------------------------------------------------//
    
    def     RemoveIf( self, condition, value ):
        self._add_condition( condition, value, '-' )
    
    #//-------------------------------------------------------//
    
    def     _add_condition( self, condition, value, operation, pre = 0 ):
        
        if __debug__:
            if (not self.is_list) and (operation != '='):
                _Error( "Append/remove operations are not allowed for none-list options." )
        
        value = _ConditionalValue( value, self )
        
        conditions_list = _ConditionsList()
        
        conditions_list.Append( self.preconditions_list )
        conditions_list.Append( condition )
        
        conditions_list.SetValue( value, operation )
        
        if pre == 0:
            self.conditions.append( conditions_list )
        else:
            self.conditions.insert( 0, conditions_list )
        
        if __debug__:
            self.Get()   # check for recursion of conditions
    
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
        
        if _is_sequence( value ):
            sep = self.separator[:]
            return sep.join( map(str,value) )
        
        return str( value )
    
    #//-------------------------------------------------------//
    
    def     __nonzero__( self ):
        if self.Get(): return 1
        return 0
    
    #//-------------------------------------------------------//
    
    def     __str__( self ):    return self.__value_str( self.Get() )
    def     Str( self ):        return self.__value_str( self.Get() )
    

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
    def     __init__( self, initial_value = 0, is_list = 0, separator = ' ', unique = 1, update_set = 0, help = None ):
        self._init_base( help, initial_value, is_list, separator, unique, update_set )
        self.initial_value = initial_value
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val ):
        
        lval = str( val ).lower()
        if lval in self.__true_strings: return 1
        if lval in self.__false_strings: return 0
        
        _Error( "Invalid boolean value: '%s'" % (val) )
    
    #//-------------------------------------------------------//
    
    def     __str__( self ):
        
        value_str = self.__invert_bool[ str( self.initial_value ).lower() ]
        
        if self == self.initial_value:
            value_str = self.__invert_bool[ value_str ]
        
        return value_str
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'yes/no, true/false, on/off, enabled/disabled, 1/0'
    
 
#//===========================================================================//
#//===========================================================================//

class   EnumOption (OptionBase):
    
    def     __init__( self, initial_value, allowed_values = None, aliases = None, is_list = 0, separator = ' ', unique = 1, help = None, update_set = 0, options = None):
        
        self.values_dict = {}
        
        self.AddValues( allowed_values )
        
        self._init_base( help, initial_value, is_list, separator, unique, update_set, options )
        
        self.AddAliases( aliases )
        
    #//-------------------------------------------------------//
    
    def     __map_values( self, values ):
        
        values_dict = self.values_dict
        
        mapped_values = []
        
        for v in _to_list( values ):
            
            v = v.lower()
            
            try:
                alias = values_dict[ v ]
            except KeyError:
                return None
            
            if alias is None:
                mapped_values.append( v )
            else:
                mapped_values += alias
        
        return mapped_values
    
    #//=======================================================//
    
    def     _convert_value( self, val ):
        
        value = self.__map_values( val )
        
        if value is None:
            _Error( "Invalid value: '%s'" % (val) )
        
        return value
    
    #//=======================================================//
    
    def     AddValues( self, values ):
        values_dict = self.values_dict
        
        for v in _to_list( values ):
            values_dict[ v.lower() ] = None
    
    #//=======================================================//
    
    def     AddAlias( self, alias, values ):
        
        mapped_values = self.__map_values( values )
        if mapped_values is None:
            _Error( "Invalid value(s): %s" % (values) )
        
        if (not self.is_list) and (_is_sequence( mapped_values ) and (len( mapped_values ) > 1)):
            _Error( "Can't add an alias to list of values: %s of none-list option" % (mapped_values) )
        
        self.values_dict[ alias ] = mapped_values
    
    #//=======================================================//
    
    def     AddAliases( self, aliases ):
        
        if not aliases:
            return
        
        if __debug__:
            if not _is_dict( aliases ):
                _Error( "Aliases must be a dictionary" )
        
        for a,v in aliases.iteritems():
            self.AddAlias( a, v )
    
    #//=======================================================//
    
    def     AllowedValues( self ):
        
        allowed_values = []
        
        for a,v in self.values_dict.iteritems():
            if v is None:
                allowed_values.append( a )
        
        return allowed_values
    
    #//=======================================================//
    
    def     Aliases( self ):
        
        aliases = {}
        
        for a,v in self.values_dict.iteritems():
            
            if v is not None:
                if len(v) == 1:
                    aliases[ v[0] ] = aliases.get( v[0], [] ) + [ a ]
            else:
                aliases.setdefault( a )
        
        return aliases
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        
        for v,a in self.Aliases().iteritems():
            
            if a is not None:
                v = v + '(or ' + 'or'.join( a ) + ')'
            
            allowed_values.append( v )
        
        return ', '.join( allowed_values )
    
    #//=======================================================//
    
    def     Clone( self, options ):
        
        clone = OptionBase.Clone( self, options )
        
        clone.values_dict = self.values_dict.copy()
        
        return clone


#//===========================================================================//
#//===========================================================================//

class   IntOption (OptionBase):
    
    def     __init__( self, initial_value, min = -(sys.maxint - 1), max = sys.maxint, is_list = 0, separator = ' ', unique = 1, update_set = 0, help = None ):
        
        self.min_value = int( min )
        self.max_value = int( max )
        
        if __debug__:
            if self.min_value > self.max_value:
                _Error( "Minimal value: %d is greater than maximal value: %d " % (min, max) )
        
        self._init_base( help, initial_value, is_list, separator, unique, update_set )
    
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
    
    def     __init__( self, initial_value = None, is_list = 0, separator = ' ', unique = 1, ignore_case = 0, update_set = 0, help = None ):
        
        if initial_value is None:
            initial_value = ''
        
        self.ignore_case = ignore_case
        self._init_base( help, initial_value, is_list, separator, unique, update_set )
    
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
    
    def     __init__( self, initial_value, options, linked_opt_name, is_list = 0, separator = ' ', unique = 1, update_set = 0, help = None ):
        
        self.linked_opt_name = linked_opt_name
        
        self._init_base( help, initial_value, is_list, separator, unique, update_set, options )
    
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
    
    def     __init__( self, initial_value = None, is_list = 0, separator = ' ', unique = 1, update_set = 0, help = None ):
        
        if initial_value is None:
            initial_value = ''
        
        self._init_base( help, initial_value, is_list, separator, unique, update_set )
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val ):
        
        return _Version( val )
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'Version in format N[a].N[a].N[a]... (where N - dec numbers, a - alphas)'

#//===========================================================================//
#//===========================================================================//

class   PathOption (OptionBase):
    
    def     __init__( self, initial_value = None, is_list = 0, separator = None, unique = 1, update_set = 0, help = None, is_node = 0 ):
        
        if initial_value is None:
            initial_value = ''
        
        if (separator is None):
            separator = os.pathsep
        
        self.is_node = is_node
        
        self._init_base( help, initial_value, is_list, separator, unique, update_set )
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val ):
        
        if ( hasattr(val, 'env' ) and hasattr(val, 'labspath' ) and hasattr(val, 'path_elements' ) ):
            # it is likely that this is a Node object, just return it as it is
            return val
        
        if self.is_node:
            env = self.options.Env()
            
            if env is not None:
                return env.Dir( val ).srcnode()
        
        return os.path.normcase( os.path.abspath( val ) )
    
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
    
    def     __add_condition( self, value, operation, condition = None, pre = 0 ):
        
        conditions_list = self.conditions_list
        
        if condition is not None:
            conditions_list = conditions_list.Clone()
            conditions_list.Append( condition )
        
        self.option._add_condition( conditions_list, value, operation, pre )
    
    #//-------------------------------------------------------//
    
    def     Set( self, value ):                     self.__add_condition( value, '=' )
    def     Preset( self, value ):                  self.__add_condition( value, '=', pre = 1 )
    def     SetIf( self, condition, value ):        self.__add_condition( value, '=', condition )
    def     PresetIf( self, condition, value ):     self.__add_condition( value, '=', condition, pre = 1 )
    def     Append( self, value ):                  self.__add_condition( value, '+' )
    def     Prepend( self, value ):                 self.__add_condition( value, '+', pre = 1 )
    def     AppendIf( self, condition, value ):     self.__add_condition( value, '+', condition )
    def     PrependIf( self, condition, value ):    self.__add_condition( value, '+', condition, pre = 1 )
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
