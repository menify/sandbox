
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
    
    def   __cmp__( self, other ):     return cmp( self.ver, Version( other ).ver )
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
    
    def   convert( self, value ):
        if value is not None:
            return self.value_type(value)
        
        return self.value_type()
    
    def   compare( self, value1, value2 ):
        
        value_type = self.value_type
        
        value1 = value_type( self )      # cast to base type to avoid recursion
        value2 = value_type( other )     # cast to base type to avoid recursion
        
        return comparator( value1, value2 )


#//---------------------------------------------------------------------------//


class   ConverterEnum (object):
    
    __slots__ = ('values', 'aliases', 'value_type')
    
    def     __init__( self, value_type ):
        self.values = []
        self.aliases = {}
        self.value_type = value_type
    
    #//-------------------------------------------------------//
    
    def   __mapValue(self, value ):
        
        value = self.value_type( value )
        
        print "values:", self.values
        if value in self.values:
            return value
        print "aliases:", self.aliases
        print "value:", type(value)
        for k,v in self.aliases.iteritems():
            print type(k), type(v)
        
        return self.aliases.get( value )
    
    #//-------------------------------------------------------//
    
    def     __call__( self, value ):
        
        value = self.value_type( value )
        
        value = self.__mapValue( value )
        if value is None:
            raise TypeError("Invalid value: %s " % value )
        
        return value
    
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

#//---------------------------------------------------------------------------//

def     createValueType( base_type, converter = None, comparator = None ):
    
    if converter is None:
        def     _convert( value ):
            if value is not None:
                value = base_type(value)
            else:
                value = base_type()
            
            print "value:", value
            
            return value
            
        converter = _convert
    
    if comparator is None:
        comparator = base_type.__cmp__
    
    #//=======================================================//
    
    class ValueType (base_type):
        
        def     __new__( cls, value = None ):
            if isinstance( value, ValueType ):
                return value    # already converted type
            
            value = converter( value )
            assert isinstance( value, base_type )
            
            self = super(ValueType, cls).__new__(cls, value )
            return self
        
        #//-------------------------------------------------------//
        
        def     __cmp__(self, other):
            other = self.__class__( other )
            
            value1 = base_type( self )      # cast to base type to avoid recursion
            value2 = base_type( other )     # cast to base type to avoid recursion
            
            return comparator( value1, value2 )
        
        #//-------------------------------------------------------//
        
        def __lt__( self, other):       return self.__cmp__(other) < 0
        def __le__( self, other):       return self.__cmp__(other) <= 0
        def __eq__( self, other):       return self.__cmp__(other) == 0
        def __ne__( self, other):       return self.__cmp__(other) != 0
        def __gt__( self, other):       return self.__cmp__(other) > 0
        def __ge__( self, other):       return self.__cmp__(other) >= 0
        
        #//-------------------------------------------------------//
        
        @staticmethod
        def     getConverter():
            return converter
        
        #//-------------------------------------------------------//
        
        @staticmethod
        def     getComparator():
            return comparator
    
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
            other = self.__class__( other )
            
            return super(self.__class__, self).__cmp__( self, other )
        
        #//-------------------------------------------------------//
        
        def __lt__( self, other):       return self.__cmp__(other) < 0
        def __le__( self, other):       return self.__cmp__(other) <= 0
        def __eq__( self, other):       return self.__cmp__(other) == 0
        def __ne__( self, other):       return self.__cmp__(other) != 0
        def __gt__( self, other):       return self.__cmp__(other) > 0
        def __ge__( self, other):       return self.__cmp__(other) >= 0
        
        #//-------------------------------------------------------//
        
        def   __add__(self, other ):
          return super(self.__class__, self).__add__( self, self.__class__(other) )
        
        def   __iadd__(self, other ):
          return super(self.__class__, self).__iadd__( self, self.__class__(other) )
        
        def   __setitem__(self, position, value ):
          return super(self.__class__, self).__setitem__( self, position, value_type( value ) )
        
        def   append( self, value ):
          return super(self.__class__, self).append( self, value_type( value ) )
        
        def   extend( self, value ):
          return super(self.__class__, self).extend( self, value_type( value ) )
        
        def   insert( self, position, value ):
          return super(self.__class__, self).insert( self, position, value_type( value ) )
    
    return ValueListType

#//===========================================================================//

if __name__ == "__main__":
    
    import string
    
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

