
import os
import sys

import utils
import logging
import version

_Error = logging.Error

#//---------------------------------------------------------------------------//

def     _is_option( option, isinstance = isinstance ):
    return isinstance( option, OptionBase )

#//---------------------------------------------------------------------------//

def     _is_options( option, isinstance = isinstance ):
    return isinstance( option, Options )

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
        self.__dict__['__cache']            = {}
    
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
            #~ if _isSequence( value ):   is_list = 1
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
    
    def     __get_option( self, name, exception_type = AttributeError ):
        option = self.__find_option( name )
        
        if option is None:
            raise exception_type( "Unknown option: '%s'" % (name) )
        
        return option
    
    #//-------------------------------------------------------//
    
    def     __list_options( self ):
        return self.__dict__['__names_dict'].iterkeys()
    
    #//-------------------------------------------------------//
    
    def     __setattr__(self, name, value):
        self.__set_option( name, value )
    
    #//-------------------------------------------------------//
    
    def     __getattr__( self, name ):
        return self.__get_option( name )
    
    #//-------------------------------------------------------//
    
    def     __setitem__( self, name, value ):
        self.__set_option( name, value )
        
    #//-------------------------------------------------------//
    
    def     __getitem__( self, name ):
        return self.__get_option( name, KeyError )
    
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
    
    def     update( self, args, quiet = 1,
                    isDict = utils.isDict,
                    isString = utils.isString ):
        
        if isString( args ):
            filename = args
            args = {}
            execfile( filename, {}, args )
        
        if isDict( args ):
            set_option = self.__set_option
            
            for key, value in args.iteritems():
                set_option( key, value, update = 1, quiet = quiet )
        else:
            _Error( "Invalid argument: %s" % (str(args)) )

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
            
            opt = id_list[0]._clone( options )
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
    
    #//-------------------------------------------------------//
    
    def     Cache( self ):
        return self.__dict__['__cache']
    
    def     ClearCache( self ):
        self.__dict__['__cache'] = {}

#//===========================================================================//
#//===========================================================================//

class   _OptionValue:
    def     __init__( self, value, option ):
        
        self.name = value.Names()[0]
        
        if __debug__:
            option.Convert( value.GetList() )      # check the current value
        
    #//-------------------------------------------------------//
    
    def     Get( self, option, opt_current_value ):
        
        opt = option.options[ self.name ]
        
        if opt is option:
            return opt_current_value
        
        return  map( option._convert_value, opt.GetList() )

#//===========================================================================//

class   _SimpleValue:
    def     __init__( self, value, option, toSequence = utils.toSequence ):
        self.value = toSequence( option._convert_value( value ) )
    
    #//-------------------------------------------------------//
    
    def     Get( self, option, opt_current_value ):
        return self.value

#//===========================================================================//

class   _Value:
    
    def     __init__( self, values, option,
                      isinstance = isinstance,
                      toSequence = utils.toSequence ):
        
        if isinstance( values, _Value ):
            self.values = values.values
            return
        
        values = toSequence( values, option.shared_data['separator'] )
        
        self_values = []
        
        for v in values:
            
            if _is_option( v ):
                v = _OptionValue( v, option )
            
            else:
                v = _SimpleValue( v, option )
            
            self_values.append( v )
        
        self.values = self_values
    
    #//-------------------------------------------------------//
    
    def     GetList( self, option, opt_current_value ):
        
        values = []
        
        for v in self.values:
            values += v.Get( option, opt_current_value )
        
        return values
    
    #//-------------------------------------------------------//
    
    def     Get( self, option, opt_current_value, len = len ):
        values = self.GetList( option, opt_current_value )
        
        if option.shared_data['is_list']:
            return values
        
        if not values:
            return None
        
        if len(values) != 1:
            _Error("Can't convert list of values: %s to non-list option: '%s'" % (values, option.Names()[0]) )
        
        return values[0]

#//===========================================================================//
#//===========================================================================//

def     _lt( op, value1, value2 ):          return value1 <  value2.GetList( op, value1 )
def     _le( op, value1, value2 ):          return value1 <= value2.GetList( op, value1 )
def     _eq( op, value1, value2 ):          return value1 == value2.GetList( op, value1 )
def     _ne( op, value1, value2 ):          return value1 != value2.GetList( op, value1 )
def     _gt( op, value1, value2 ):          return value1 >  value2.GetList( op, value1 )
def     _ge( op, value1, value2 ):          return value1 >= value2.GetList( op, value1 )

#//-------------------------------------------------------//

def     _has( op, values1, values2 ):
    
    for v in values2.GetList( op, values1 ):
        if v not in values1:
            return 0
    
    return 1

#//-------------------------------------------------------//

def     _has_any( op, values1, values2 ):
    
    for v in values2.GetList( op, values1 ):
        if v in values1:
            return 1
    
    return 0

#//-------------------------------------------------------//

def     _one_of( op, value1, values2 ):
    
    values2 = values2.GetList( op, value1 )
    
    for v in value1:
        if v not in values2:
            return 0
    
    return 1

#//===========================================================================//

def     _always_true_condition( options, op, current_value ):
    return 1

#//===========================================================================//

class   _Condition:
    
    def     __init__( self, name, cond_function, value ):
        self.name = name
        self.cond_function = cond_function
        self.value =  value
    
    #//-------------------------------------------------------//
    
    def     __call__( self, options, op, current_value ):
        
        option = options[ self.name ]
        
        if option is not op:
            current_value = option.GetList()
        
        return self.cond_function( option, current_value, self.value )

#//===========================================================================//
#//===========================================================================//

class   _ConditionalValue:
    
    def    __init__( self ):
        self.conditions = []
        self.value = None
        self.operation = None
    
    #//-------------------------------------------------------//
    
    def     Append( self, cond ):
        
        if isinstance( cond, _ConditionalValue ):
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
    
    def     IsTrue( self, options, op, current_value ):
        for c in self.conditions:
            if not c( options, op, current_value ):
                return 0
        
        return 1
    
    #//-------------------------------------------------------//
    
    def     Clone( self ):
        clone = _ConditionalValue()
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
    def     Cache( self ):                      return {}
    def     ClearCache( self ):                 pass

_none_options = _NoneOptions()

#//===========================================================================//
#//===========================================================================//

class   OptionBase:
    
    def     _init_base( self, **kw ):
        
        kw.setdefault( 'help', None )
        kw.setdefault( 'group', "User" )
        kw.setdefault( 'initial_value', None )
        
        is_list = kw.setdefault( 'is_list', 0 )
        
        if is_list:
            kw.setdefault( 'separator', ' ' )
        else:
            kw.setdefault( 'separator', '' )
        
        kw.setdefault( 'unique', 1 )
        
        if is_list:
            update = kw.setdefault( 'update', 'Append' )
        else:
            update = 'Set'
            kw['update'] = update
        
        self.Update = getattr( self, update )
        
        self.options = kw.get( 'options', _none_options )
        
        self.shared_data = kw
        
        self.conditions = []
    
    #//-------------------------------------------------------//
    
    def     _set_default( self ):
        
        if self.shared_data[ 'is_list' ]:
            self.Append( self.shared_data[ 'initial_value' ] )
        else:
            self.Set( self.shared_data[ 'initial_value' ] )
    
    #//-------------------------------------------------------//
    
    def     _clone( self, options ):
        clone = OptionBase()
        
        clone.__dict__ = self.__dict__.copy();
        clone.__class__ = self.__class__;
        
        clone.options = options
        clone.conditions = self.conditions[:]
        
        clone.Update = getattr( clone, clone.shared_data[ 'update' ] )
        
        return clone
    
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
    
    def     GetList( self,
                     appendToList = utils.appendToList,
                     removeFromList = utils.removeFromList,
                     id = id ):
        
        cache = self.options.Cache()
        id_self = id(self)
        
        values = cache.get( id_self )
        if values is not None:
            return values
        
        values = []
        
        unique = self.shared_data['unique']
        options = self.options
        
        for c in self.conditions:
            if c.IsTrue( options, self, values ):
                
                op, v = c.GetValue()
                v = v.GetList( self, values )
                
                if op == '=':
                    values = v
                
                elif op == '+':
                    appendToList( values, v, unique )
                
                elif op == '-':
                    removeFromList( values, v )
        
        cache[ id_self ] = values
        
        return values
    
    #//-------------------------------------------------------//
    
    def     Get( self ):
        
        values = self.GetList()
        
        if self.shared_data['is_list']:
            return values
            
        if not values:
            return None
        
        return values[0]
    
    #//-------------------------------------------------------//
    
    def     Set( self, value ):
        self.SetIf( _always_true_condition, value )
    
    #//-------------------------------------------------------//
    
    def     Preset( self, value ):
        self.PresetIf( _always_true_condition, value )
    
    #//-------------------------------------------------------//
    
    def     Append( self, value ):
        self.AppendIf( _always_true_condition, value )
    
    #//-------------------------------------------------------//
    
    def     Prepend( self, value ):
        self.PrependIf( _always_true_condition, value )
    
    #//-------------------------------------------------------//
    
    def     Remove( self, value ):
        self.RemoveIf( _always_true_condition, value )
    
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
            if (not self.shared_data['is_list']) and (operation != '='):
                _Error( "Append/remove operations are not allowed for none-list options." )
        
        value = _Value( value, self )
        
        conditional_value = _ConditionalValue()
        conditional_value.Append( condition )
        
        conditional_value.SetValue( value, operation )
        
        if not pre:
            if (operation == '=') and (condition is _always_true_condition):
                self.conditions = []                                    # clear the conditions list if it's an unconditional set
            
            self.conditions.append( conditional_value )
        else:
            self.conditions.insert( 0, conditional_value )
        
        self.options.ClearCache()
    
    #//-------------------------------------------------------//
    
    def     Convert( self, value ):
        if value is self:
            return self.Get()
        
        return _Value( value, self ).Get( self, None )
    
    def     __lt__( self, other):       return _lt( self, self.GetList(), _Value( other, self ) )
    def     __le__( self, other):       return _le( self, self.GetList(), _Value( other, self ) )
    def     __eq__( self, other):       return _eq( self, self.GetList(), _Value( other, self ) )
    def     __ne__( self, other):       return _ne( self, self.GetList(), _Value( other, self ) )
    def     __gt__( self, other):       return _gt( self, self.GetList(), _Value( other, self ) )
    def     __ge__( self, other):       return _ge( self, self.GetList(), _Value( other, self ) )
    
    def     __contains__(self, other):  return self.has( other )
    def     has( self, other ):         return _has( self, self.GetList(), _Value( other, self ) )
    def     has_any( self, other ):     return _has_any( self, self.GetList(), _Value( other, self ) )
    def     one_of( self, values ):     return _one_of( self, self.GetList(), _Value( values, self ) )
    
    #//-------------------------------------------------------//
    
    def     __nonzero__( self ):
        if self.Get(): return 1
        return 0
    
    #//-------------------------------------------------------//
    
    def     isSetNotTo( self, value ):
        self_value = self.GetList()
        
        if self_value:
            value = _Value( value, self ).GetList( self, self_value )
            
            if self_value != value:
                return True
        
        return False
    
    #//-------------------------------------------------------//
    
    def     isNotSetOr( self, value ):
        return not self.isSetNotTo( value )
    
    #//-------------------------------------------------------//
    
    def     __str__( self, map = map, str = str ):
        return self.shared_data['separator'].join( map(str, self.GetList() ) )


#//===========================================================================//
#//===========================================================================//

class   BoolOption (OptionBase):
    
    __invert_true = {
               'y': 'no',
               'yes': 'no',
               't': 'false',
               '1': 'false',
               'true': 'false',
               'on': 'off',
               'enabled' : 'disabled' }
               
    __invert_false = {
               'n': 'yes',
               'no': 'yes',
               'f': 'true',
               '0': 'true',
               'false': 'true',
               'off': 'on',
               'disabled' : 'enabled',
               'none' : 'true'
             }
    
    __invert_bool = __invert_true.copy()
    __invert_bool.update( __invert_false )
    
    #//-------------------------------------------------------//
    def     __init__( self, **kw ):
        
        self._init_base( **kw )
        self._set_default()
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val,
                            str = str,
                            invert_true = __invert_true,
                            invert_false = __invert_false ):
        
        lval = str( val ).lower()
        if invert_true.has_key( lval ):     return 1
        if invert_false.has_key( lval ):    return 0
        
        _Error( "Invalid boolean value: '%s'" % (val) )
    
    #//-------------------------------------------------------//
    
    def     __str__( self ):
        
        initial_value = self.shared_data['initial_value']
        
        value_str = self.__invert_bool[ str( initial_value ).lower() ]
        
        if self == initial_value:
            value_str = self.__invert_bool[ value_str ]
        
        return value_str
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'yes/no, true/false, on/off, enabled/disabled, 1/0'
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesHelp( self ):
        if self.shared_data['is_list']:
            return 'List of boolean values: ' + self.AllowedValuesStr()
        
        return 'A boolean value: ' + self.AllowedValuesStr()
    

#//===========================================================================//
#//===========================================================================//

class   EnumOption (OptionBase):
    
    def     __init__( self, **kw ):
        
        kw['values_dict'] = {}
        
        aliases = kw.get( 'aliases', {} )
        allowed_values = kw.get( 'allowed_values', () )
        
        self._init_base( **kw )
        
        self.AddValues( allowed_values )
        self.AddAliases( aliases )
        
        self._set_default()
        
    #//-------------------------------------------------------//
    
    def     __map_values( self, values, toSequence = utils.toSequence ):
        
        values_dict = self.shared_data['values_dict']
        
        mapped_values = []
        
        for v in toSequence( values ):
            
            try:
                v = v.lower()
                alias = values_dict[ v ]
            
            except (AttributeError, KeyError):
                return None
            
            if alias is None:
                mapped_values.append( v )
            else:
                mapped_values += alias
        
        return mapped_values
    
    #//=======================================================//
    
    def     _convert_value( self, val ):
        
        value = self.__map_values( val )
        
        if not value:
            _Error( "Invalid value: '%s', type: %s" % (val, type(val)) )
        
        return value
    
    #//=======================================================//
    
    def     AddValues( self, values, toSequence = utils.toSequence ):
        values_dict = self.shared_data['values_dict']
        
        for v in toSequence( values ):
            
            try:
                values_dict[ v.lower() ] = None
            
            except AttributeError:
                _Error( "Invalid value: '%s', type: %s" % (val, type(val)) )
    
    #//=======================================================//
    
    def     AddAlias( self, alias, values, isSequence = utils.isSequence ):
        
        mapped_values = self.__map_values( values )
        if not mapped_values:
            _Error( "Invalid value(s): %s" % (values) )
        
        if (not self.shared_data['is_list']) and (isSequence( mapped_values ) and (len( mapped_values ) > 1)):
            _Error( "Can't add an alias to list of values: %s of none-list option" % (mapped_values) )
        
        self.shared_data['values_dict'][ alias ] = mapped_values
    
    #//=======================================================//
    
    def     AddAliases( self, aliases,
                        isDict = utils.isDict ):
        
        if not aliases:
            return
        
        if __debug__:
            if not isDict( aliases ):
                _Error( "Aliases must be a dictionary" )
        
        for a,v in aliases.iteritems():
            self.AddAlias( a, v )
    
    #//=======================================================//
    
    def     AllowedValues( self ):
        
        allowed_values = []
        
        for a,v in self.shared_data['values_dict'].iteritems():
            if v is None:
                allowed_values.append( a )
        
        return allowed_values
    
    #//=======================================================//
    
    def     Aliases( self ):
        
        aliases = {}
        
        for a,v in self.shared_data['values_dict'].iteritems():
            
            if v is not None:
                if len(v) == 1:
                    tmp = aliases.get( v[0] )
                    if tmp:
                        aliases[ v[0] ] = tmp + [ a ]
                    else:
                        aliases[ v[0] ] = [ a ]
            else:
                aliases.setdefault( a )
        
        return aliases
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        
        allowed_values = []
        
        aliases = self.Aliases()
        values = aliases.keys()
        values.sort()
        
        for v in values:
            
            a = aliases[v]
            
            if a is not None:
                a.sort()
                v = v + ' (or ' + ', '.join( a ) + ')'
            
            allowed_values.append( v )
        
        return ', '.join( allowed_values )
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesHelp( self ):
        if self.shared_data['is_list']:
            return 'List of values: ' + self.AllowedValuesStr()
        
        return 'A value: ' + self.AllowedValuesStr()
    


#//===========================================================================//
#//===========================================================================//

class   IntOption (OptionBase):
    
    def     __init__( self, **kw ):
        
        kw['min'] = int( kw.get( 'min', -(sys.maxint - 1) ) )
        kw['max'] = int( kw.get( 'max', sys.maxint ) )
        
        if __debug__:
            if kw['min'] > kw['max']:
                _Error( "Minimal value: %d is greater than maximal value: %d " % (min, max) )
        
        self._init_base( **kw )
        self._set_default()
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val ):
        
        try:
            int_val = int(val)
        
        except TypeError:
            _Error( "Invalid type of value: %s, type: %s" % (val, type(val)) )
        
        if (int_val < self.shared_data['min']) or (int_val > self.shared_data['max']):
            _Error( "Invalid value: %s" % (val) )
        
        return int_val
    
    #//-------------------------------------------------------//
    
    def     __int__( self ):
        return self.Get()
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return '%d ... %d' % (self.shared_data['min'], self.shared_data['max'])
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesHelp( self ):
        if self.shared_data['is_list']:
            return 'List of integers from: ' + self.AllowedValuesStr()
        
        return 'An integer from: ' + self.AllowedValuesStr()


#//===========================================================================//
#//===========================================================================//

class   StrOption (OptionBase):
    
    def     __init__( self, **kw ):
        
        kw.setdefault( 'ignore_case', 0 )
        
        self._init_base( **kw )
        self._set_default()
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, value ):
        
        if value is None:
            return ''
        
        value = str(value)
        if self.shared_data['ignore_case']:
            value = value.lower()
        
        return value
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'string'

    #//-------------------------------------------------------//
    
    def     AllowedValuesHelp( self ):
        if self.shared_data['is_list']:
            return 'List of strings'
        
        return 'A string'


#//===========================================================================//
#//===========================================================================//

class   LinkedOption (OptionBase):
    
    def     __init__( self, **kw ):
        
        if not kw.get( 'linked_opt_name' ):
            _Error('Linked option name has not been passed. linked_opt_name is not set. ')
        
        self._init_base( **kw )
        self._set_default()
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, value ):
        
        linked_option = self.options[ self.shared_data['linked_opt_name'] ]
        
        return linked_option._convert_value( value )
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        linked_option = self.options[ self.shared_data['linked_opt_name'] ]
        return linked_option.AllowedValuesStr()
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesHelp( self ):
        if self.shared_data['is_list']:
            return 'List of values: ' + self.AllowedValuesStr()
        
        return 'A value: ' + self.AllowedValuesStr()


#//===========================================================================//
#//===========================================================================//

class   VersionOption (OptionBase):
    
    def     __init__( self, **kw ):
        
        self._init_base( **kw )
        self._set_default()
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val, _Version = version.Version ):
        return _Version( val )
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'Version in format N[a].N[a].N[a]... (where N - dec numbers, a - alphas)'
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesHelp( self ):
        if self.shared_data['is_list']:
            return 'List: ' + self.AllowedValuesStr()
        
        return self.AllowedValuesStr()

#//===========================================================================//
#//===========================================================================//

class   PathOption (OptionBase):
    
    def     __init__( self, **kw ):
        
        kw.setdefault( 'separator', os.pathsep )
        kw.setdefault( 'is_node', 0 )
        
        self._init_base( **kw )
        self._set_default()
    
    #//-------------------------------------------------------//
    
    def     _convert_value( self, val,
                            hasattr = hasattr,
                            normcase = os.path.normcase,
                            abspath = os.path.abspath ):
        
        if (hasattr( val, 'env' ) and hasattr( val, 'labspath' ) and hasattr( val, 'path_elements' )):
            # it is likely that this is a Node object, just return it as it is
            return val
        
        if val is None:
            _Error( "Invalid value: %s, type: %s" % (val, type(val)) )
        
        if self.shared_data['is_node']:
            env = self.options.Env()
            
            if env is not None:
                return env.Dir( val ).srcnode()
        
        return normcase( abspath( val ) )
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesStr( self ):
        return 'A file system path'
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesHelp( self ):
        if self.shared_data['is_list']:
            return 'List of file system paths'
        
        return 'A file system path'

#//===========================================================================//
#//===========================================================================//

class _ConditionalOptions:
    
    def     __init__( self, options, conditional_value = None ):
        
        self.__dict__['__options'] = options
        
        if conditional_value is not None:
            self.__dict__['__conditional_value'] = conditional_value.Clone()
        else:
            self.__dict__['__conditional_value'] = _ConditionalValue()
    
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
        
        option.SetIf( self.__dict__['__conditional_value'], value )
    
    #//-------------------------------------------------------//
    
    def     __setitem__( self, name, value ):
        self.__setattr__( name, value )
    
    #//-------------------------------------------------------//
    
    def     __getattr__( self, name ):
        
        options = self.__dict__['__options']
        option = options.get( name )
        
        if option is None:
            _Error( "Unknown option: %s" % (name) )
        
        return _ConditionalOption( name, option, options, self.__dict__['__conditional_value'] )
    
    #//-------------------------------------------------------//
    
    def     __getitem__(self, name ):
        return self.__getattr__( name )
    
    #//-------------------------------------------------------//
    
    def     __repr__( self ):
        return "<_Conditional Options>"

#//===========================================================================//
#//===========================================================================//

class   _ConditionalOption:
    
    def     __init__( self, name, option, options, conditional_value ):
        
        self.name = name
        self.option = option
        self.options = options
        self.conditional_value = conditional_value
    
    #//-------------------------------------------------------//
    
    def     __add_condition( self, value, operation, condition = None, pre = 0 ):
        
        conditional_value = self.conditional_value
        
        if condition is not None:
            conditional_value = conditional_value.Clone()
            conditional_value.Append( condition )
        
        self.option._add_condition( conditional_value, value, operation, pre )
    
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
        
        if self.option.shared_data['is_list']:
            return self.has( value )
        
        return self.eq( value )
    
    #//-------------------------------------------------------//
    
    def     __cond_options( self, cond_function, value ):
        
        conditional_value = self.conditional_value.Clone()
        
        value = _Value( value, self.option )
        conditional_value.Append( _Condition( self.name, cond_function, value ) )
        
        return _ConditionalOptions( self.options, conditional_value )
    
    #//-------------------------------------------------------//
    
    def     has( self, value ):         return self.__cond_options( _has, value )
    def     has_any( self, values ):    return self.__cond_options( _has_any, values )
    def     one_of( self, values ):     return self.__cond_options( _one_of, values )
    def     eq( self, value ):          return self.__cond_options( _eq, value )
    def     ne( self, value ):          return self.__cond_options( _ne, value )
    def     gt( self, value ):          return self.__cond_options( _gt, value )
    def     ge( self, value ):          return self.__cond_options( _ge, value )
    def     lt( self, value ):          return self.__cond_options( _lt, value )
    def     le( self, value ):          return self.__cond_options( _le, value )
