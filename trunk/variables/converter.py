
import re

#13.10.3077
#8.00v
#4.1.1
#1.6
#8.42n
#5.5.1

class   Version (str):
    def     __new__(cls, version = None, _ver_re = re.compile(r'[0-9]+[a-zA-Z]*(\.[0-9]+[a-zA-Z]*)*') ):
        
        if isinstance(version, Version):
            return version
        
        if version is None:
            ver_str = ''
        else:
            ver_str = str(version)
        
        match = _ver_re.search( ver_str )
        if match:
            ver_str = match.group()
            ver_list = re.findall(r'[0-9]+|[a-zA-Z]+', ver_str )
        else:
            ver_str = ''
            ver_list = []
        
        self = super(Version, cls).__new__(cls, ver_str )
        conv_ver_list = []
        
        for v in ver_list:
            if v.isdigit():
                v = int(v)
            conv_ver_list.append( v )
        
        self.__version = conv_ver_list
        
        return self
    
    #//-------------------------------------------------------//
    
    def   __cmp__( self, other ):     return cmp( self.__version, Version( other ).__version )
    def   __lt__( self, other):       return self.__cmp__(other) < 0
    def   __le__( self, other):       return self.__cmp__(other) <= 0
    def   __eq__( self, other):       return self.__cmp__(other) == 0
    def   __ne__( self, other):       return self.__cmp__(other) != 0
    def   __gt__( self, other):       return self.__cmp__(other) > 0
    def   __ge__( self, other):       return self.__cmp__(other) >= 0


#//---------------------------------------------------------------------------//

class TypeTraitsBase (object):
    def   __init__(self, value_type):
        self.value_type = value_type
    
    #//-------------------------------------------------------//
    
    def   convert( self, value ):
        print "TypeTraitsBase.convert"
        if value is not None:
            return self.value_type(value)
        
        return self.value_type()
    
    #//-------------------------------------------------------//
    
    def   compare( self, value1, value2 ):
        assert isinstance( value1, self.value_type )
        assert isinstance( value2, self.value_type )
        
        return cmp( value1, value2 )
    
    #//-------------------------------------------------------//
    
    def   hash( self, value ):
        assert isinstance( value, self.value_type )
        return hash( value )
    
    #//-------------------------------------------------------//
    
    def     getValueType(self):
        return self.value_type;

#//---------------------------------------------------------------------------//

class IgnoreCaseStrTraits (TypeTraitsBase):
    
    def   compare( self, value1, value2 ):
        assert issubclass( self.value_type, str )
        assert isinstance( value1, self.value_type )
        assert isinstance( value2, self.value_type )
        
        return cmp( value1.lower(), value2.lower() )
    
    #//-------------------------------------------------------//
    
    def   hash( self, value ):
        assert issubclass( self.value_type, str )
        assert isinstance( value, self.value_type )
        
        return hash( value.lower() )

#//---------------------------------------------------------------------------//

class LowerCaseStrTraits (TypeTraitsBase):
    def   convert( self, value ):
        assert issubclass( self.value_type, str )
        
        print "LowerCaseStrTraits.convert"
        return super(LowerCaseStrTraits, self).convert( value ).lower()

#//---------------------------------------------------------------------------//

class CapitalStrTraits (TypeTraitsBase):
    def   convert( self, value ):
        assert issubclass( self.value_type, str )
        
        print "CapitalStrTraits.convert"
        value = super(CapitalStrTraits, self).convert( value )
        return value[:1].upper() + value[1:].lower()

#//---------------------------------------------------------------------------//

class   EnumTypeTraits (TypeTraitsBase):
    
    def     __init__( self, value_type ):
        super(EnumTypeTraits, self).__init__( value_type )
        
        self.values = []
        self.aliases = {}
        self.value_type = value_type
    
    #//-------------------------------------------------------//
    
    def   __mapValue(self, value ):
        
        value = self.value_type( value )
        
        if value in self.values:
            return value
        
        for k,v in self.aliases.iteritems():
            print type(k), type(v)
        
        return self.aliases.get( value )
    
    #//-------------------------------------------------------//
    
    def     convert( self, value ):
        print "EnumTypeTraits.convert"
        
        value = super(EnumTypeTraits, self).convert( value )
        
        value = self.__mapValue( value )
        if value is None:
            raise TypeError("Invalid value: %s " % value )
        
        return value
    
    #//-------------------------------------------------------//
    
    def   compare( self, value1, value2 ):
        return cmp( value1, value2 )
    
    #//-------------------------------------------------------//
    
    def   hash( self, value ):
        return hash( value )
    
    #//-------------------------------------------------------//
    
    def   addValue( self, value ):
        
        value = self.value_type( value )
        
        if self.__mapValue( value ) is not None:
            raise TypeError("Value '%s' is already added " % value )
        
        self.values.append( value )
    
    #//-------------------------------------------------------//
    
    def   addAlias( self, value, alias ):
        
        value = self.__mapValue( value )
        if value is None:
            raise TypeError("Value '%s' is not valid" % value )
        
        alias = self.value_type( alias )
        
        alias_value = self.__mapValue( alias )
        if alias_value is not None:
            raise TypeError("Alias '%s' is already added" % alias )
        
        self.aliases[ alias ] = value
    
    #//-------------------------------------------------------//
    
    def   getValues( self ):
        return tuple( self.values )
    
    #//-------------------------------------------------------//
    
    def   getAliases( self ):
        return dict(self.aliases)

#//===========================================================================//

class   BoolTypeTraits (TypeTraitsBase):
    
    #//-------------------------------------------------------//
    
    __str_to_bool = {
               'y': True,
               'yes': True,
               't': True,
               '1': True,
               'true': True,
               'on': True,
               'enabled' : True
               
               }
    
    #//-------------------------------------------------------//
    
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
    
    #//-------------------------------------------------------//
    
    __invert_bool = __invert_true.copy()
    __invert_bool.update( __invert_false )
    
    #//-------------------------------------------------------//
    
    def     __init__( self, value_type ):
        super(EnumTypeTraits, self).__init__( value_type )
        
        self.value_type = int # don't care about value_type it's always 'int'
    
    #//-------------------------------------------------------//
    
    def     convert( self, value ):
        value = super(EnumTypeTraits, self).convert( value )
        
        if type(value) is bool:
            value = int(value)
        
        if type(value) is int:
            value = int(not not value)
        
        else:
            value_str = str(value).lower()
            if invert_true.has_key( value_str ):
                value = int(True)
            elif invert_false.has_key( value_str ):
                value = int(False)
            else:
                raise TypeError("Invalid value: %s " % value )
        
        return value
    
    #//-------------------------------------------------------//
    
    def   compare( self, value1, value2 ):
        return cmp( value1, value2 )
    
    #//-------------------------------------------------------//
    
    def   hash( self, value ):
        return hash( value )


#//===========================================================================//

def     createValueTraits( base_type, *traits ):
    return type('ValueTraits', traits, {} )( base_type )

#//---------------------------------------------------------------------------//

def     createValueType( value_type_traits ):
    
    #//=======================================================//
    
    base_type = value_type_traits.getValueType()
    
    class ValueType (base_type):
        
        def     __new__( cls, value = None ):
            if isinstance( value, ValueType ):
                return value    # already converted type
            
            value = value_type_traits.convert( value )
            assert isinstance( value, base_type )
            
            self = super(ValueType, cls).__new__(cls, value )
            return self
        
        #//-------------------------------------------------------//
        
        def     __cmp__(self, other):
            other = ValueType( other )
            return value_type_traits.compare( base_type( self ), base_type( other ) )     # cast to base type to avoid recursion
        
        def     __hash__(self ):
            return value_type_traits.hash( base_type( self ) )          # cast to base type to avoid recursion
        
        #//-------------------------------------------------------//
        
        def __lt__( self, other):       return self.__cmp__(other) < 0
        def __le__( self, other):       return self.__cmp__(other) <= 0
        def __eq__( self, other):       return self.__cmp__(other) == 0
        def __ne__( self, other):       return self.__cmp__(other) != 0
        def __gt__( self, other):       return self.__cmp__(other) > 0
        def __ge__( self, other):       return self.__cmp__(other) >= 0
    
    return ValueType

def     createValueListType( value_type ):
    
    #//=======================================================//
    
    class ValueListType (list):
        
        def     __new__( cls, value_list = None ):
            if isinstance( value_list, ValueListType ):
                return value_list    # already converted type
            
            self = super(ValueListType, cls).__new__( cls )
            
            if (value_list is not None) and ( not isinstance( value, (list, tuple) )):
                raise TypeError( "'%s' object is not iterable" % type(value_list) )
                
            self[:] = map( value_type, value_list )
            
            return self
        
        #//-------------------------------------------------------//
        
        def     __cmp__(self, other):
            other = ValueListType( other )
            
            return super(ValueListType, self).__cmp__( self, other )
        
        #//-------------------------------------------------------//
        
        def __lt__( self, other):       return self.__cmp__(other) < 0
        def __le__( self, other):       return self.__cmp__(other) <= 0
        def __eq__( self, other):       return self.__cmp__(other) == 0
        def __ne__( self, other):       return self.__cmp__(other) != 0
        def __gt__( self, other):       return self.__cmp__(other) > 0
        def __ge__( self, other):       return self.__cmp__(other) >= 0
        
        #//-------------------------------------------------------//
        
        def   __add__(self, other ):
          return super(ValueListType, self).__add__( self, ValueListType(other) )
        
        def   __iadd__(self, other ):
          return super(ValueListType, self).__iadd__( self, ValueListType(other) )
        
        def   __setitem__(self, position, value ):
          return super(ValueListType, self).__setitem__( self, position, value_type( value ) )
        
        def   append( self, value ):
          return super(ValueListType, self).append( self, value_type( value ) )
        
        def   extend( self, value ):
          return super(ValueListType, self).extend( self, value_type( value ) )
        
        def   insert( self, position, value ):
          return super(ValueListType, self).insert( self, position, value_type( value ) )
    
    return ValueListType

#//===========================================================================//

if __name__ == "__main__":
    
    import string
    
    str_traits = createValueTraits( str, CapitalStrTraits, IgnoreCaseStrTraits )
    name_type = createValueType( str_traits )
    
    enum_traits = createValueTraits( name_type, EnumTypeTraits )
    enum_traits.addValue("Tom")
    enum_traits.addValue("Ben")
    enum_traits.addAlias("tom", "Tommy")
    
    known_names_type = createValueType( enum_traits )
    print known_names_type("tommy")
    
    
    def     _cmp( a, b ):
        return cmp( a.lower()[0], b.lower()[0] )
    
    print Version
    
    ValVer = createValueType( Version )
    print ValVer("12.1")
    print ValVer("12.1") == ValVer("12.11")
    
    ValStr = createValueType( str, comparator = _cmp )
    ValInt = createValueType( int, comparator = lambda a, b: cmp(a,b) )
    ValInt = createValueType( ValInt, converter = lambda a, vt = ValInt : vt(a + (a & 1)) )
    
    print "v: '" + ValStr( None ) + "'"
    print "v: '" + ValStr( "ABC" ) + "'"
    print "v: '" + ValStr( "bEE" ) + "'"
    print ValStr( "aBC" ) == ValStr( "abc" )
    print ValStr( "bde" ) == ValStr( "b00" )
    print ValStr( "ccc" ) == ValStr( "Ccc" )
    print ValInt( 4 )
    print ValInt( 7 )
    print ValInt( 4 ) == ValInt( 3 )
    
    enum_conv = ConverterEnum( ValStr )
    enum_conv.addValue( 'abc' )
    #~ enum_conv.addValue( 'Abc' )
    enum_conv.addValue( 'bde' )
    enum_conv.addAlias( 'ABC', 'dba' )
    
    print enum_conv('DBA')
    
    ValEnumStr = createValueType( ValStr, enum_conv )
    
    
#~ class   ConverterString (Converter):
    #~ """
    #~ Converts a value into a string value
    #~ """
    
    #~ #//-------------------------------------------------------//
    
    #~ def     __init__(self, compare_func = None, convert_func = None )
        #~ if compare_func is None:
            #~ compare_func = cmp
        
        #~ def     _convert( value ):
            #~ if value is not None:
                #~ value = str(value)
            #~ else:
                #~ value = str()
        
        #~ if convert_func is None:
            #~ convert_func = _strConverter
        #~ else:
            #~ convert_func = lambda value, convert_func = convert_func, _convert = _convert: convert_func( _convert(value) )
        
        #~ Converter.__init__( self, str, compare_func, convert_func )
    
    #~ #//-------------------------------------------------------//
    
    #~ def   toString( self, value ):
        #~ return self.convert( value )
    
    #~ def   typeHelp( self, value ):
        #~ return "String"
    
    #~ def   valuesHelp( self, value ):
        #~ return "String"


#~ class   ConverterEnum (Converter):
    #~ """
    #~ Converts a value into a string value
    #~ """
    
    #~ #//-------------------------------------------------------//
    
    #~ class __Value (object):
        #~ __slots__ = ('value', 'aliases', 'compare_func')
        
        #~ #//-------------------------------------------------------//
        
        #~ def     __init__(self, value, compare_func ):
            #~ self.value = value
            #~ self.aliases = []
            #~ self.compare_func = compare_func
        
        #~ #//-------------------------------------------------------//
        
        #~ def     get(self):
            #~ return self.value
        
        #~ #//-------------------------------------------------------//
        
        #~ def     __eq__(self, other):
            #~ cmp_func = self.compare_func
            
            #~ for value in [self.value] + self.aliases:
                #~ result = cmp_func( value, other )
                #~ if result == 0:
                    #~ return True
            
            #~ return False
        
        #~ #//-------------------------------------------------------//
        
        #~ def     __ne__(self, other):
            #~ return not self.__eq__(other)
        
        #~ #//-------------------------------------------------------//
        
        #~ def     __cmp__(self, other):
            #~ if self == other:
                #~ return 0
            #~ return self.compare_func( self.value, other )
        
        #~ #//-------------------------------------------------------//
        
        #~ def     addAlias( self, alias ):
            #~ if self != other:
                #~ self.aliases.append( alias )
    
    #~ #//-------------------------------------------------------//
    
    #~ def     __init__(self, type_converter )
        
        #~ self.type_converter = type_converter
        #~ self.allowed_values = {}
        
        #~ def     _convert( value ):
            
        
        #~ convert_func = 
        
        
        #~ Converter.__init__( self, type_converter.base_type, type_converter.compare_func, convert_func )
        
        #~ if comparator is None:
            #~ comparator = cmp
        
        #~ def     _strConverter( value ):
            #~ if value is not None:
                #~ value = str(value)
            #~ else:
                #~ value = str()
        
        #~ if converter is None:
            #~ converter = _strConverter
        #~ else:
            #~ converter = lambda value, converter = converter, _strConverter = _strConverter: converter( _strConverter(value) )
    
    #~ #//-------------------------------------------------------//
    
    #~ def   toString( self, value ):
        #~ return self.convert( value )
    
    #~ def   typeHelp( self, value ):
        #~ return "String"
    
    #~ def   valuesHelp( self, value ):
        #~ return "String"

