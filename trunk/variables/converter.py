def     createValueType( base_type, converter = None, comparator = None ):
    
    if converter is None:
        def     _convert( value ):
            if value is not None:
                value = base_type(value)
            else:
                value = base_type()
            
            return value
            
        converter = _convert
    
    if comparator is None:
        comparator = base_type.__cmp__
    
    class ValueType (base_type):
        
        def     __new__( cls, value = None ):
            if isinstance( value, cls ):
                return value    # already converted type
            
            value = converter( value )
            assert isinstance( value, base_type )
            
            return super(cls, cls).__new__(cls, value)
        
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
        
        //-------------------------------------------------------//
        
        @staticmethod
        def     getComparator():
            return comparator
    
    return ValueType

#//===========================================================================//

if __name__ == "__main__":
    
    import string
    
    def     _cmp( a, b ):
        print "cmp:", a, b
        return cmp( a[0], b[0] )
    
    ValStr = createValueType( str, comparator = _cmp )
    
    #~ print "v: '" + ValStr( None ) + "'"
    print "v: '" + ValStr( "ABC" ) + "'"
    print "v: '" + ValStr( "bEE" ) + "'"
    print ValStr( "aBC" ) == ValStr( "abc" )
    print ValStr( "bde" ) == ValStr( "b00" )
    print ValStr( "ccc" ) == ValStr( "Ccc" )


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

