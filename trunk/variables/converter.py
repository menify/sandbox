
def     createBaseType( base_type, converter ):
    class BaseType (base_type):
        
        __converter = converter
        
        def     __cmp__(base_self, other):
            return BaseType.__converter.compare(base_self, other)
        
        def     __str__(self):
            return BaseType.__converter.toString( self )
    
    return BaseType

class   Converter:
    """
    A base class to convert a value into base value (string, int, bool, node and etc.)
    """
    
    #//-------------------------------------------------------//
    
    def   __init__(self, base_type, compare_func, convert_func )
        
        assert base_type
        assert convert_func
        assert compare_func
        
        self.base_type = createBaseType( base_type, self )
        self.compare_func = compare_func
        self.convert_func = convert_func
    
    #//-------------------------------------------------------//
    
    def   convert( self, value, isinstance = isinstance ):
        if isinstance( value, self.base_type ):
            return value
        
        value = self.convert_func( value )
        
        return self.base_type( value )
    
    #//-------------------------------------------------------//
    
    def   compare( self, value1, value2 ):
        value1 = self.convert( value1 )
        value2 = self.convert( value2 )
        
        value1 = value1.__class__.__bases__[0]( value1 )    # cast to base type to avoid recursion
        value2 = value2.__class__.__bases__[0]( value2 )    # cast to base type to avoid recursion
        
        return self.compare_func( value1, value2 )
    
    #//-------------------------------------------------------//
    
    def   toString( self, value ):
        raise TypeError("Abstract method. Should be implemented in child classes")4
    
    def   typeHelp( self, value ):
        raise TypeError("Abstract method. Should be implemented in child classes")
    
    def   valuesHelp( self, value ):
        raise TypeError("Abstract method. Should be implemented in child classes")

#//===========================================================================//

base_type( value )


class   ConverterString (Converter):
    """
    Converts a value into a string value
    """
    
    #//-------------------------------------------------------//
    
    def     __init__(self, compare_func = None, convert_func = None )
        if compare_func is None:
            compare_func = cmp
        
        def     _convert( value ):
            if value is not None:
                value = str(value)
            else:
                value = str()
        
        if convert_func is None:
            convert_func = _strConverter
        else:
            convert_func = lambda value, convert_func = convert_func, _convert = _convert: convert_func( _convert(value) )
        
        Converter.__init__( self, str, compare_func, convert_func )
    
    #//-------------------------------------------------------//
    
    def   toString( self, value ):
        return self.convert( value )
    
    def   typeHelp( self, value ):
        return "String"
    
    def   valuesHelp( self, value ):
        return "String"


class   ConverterEnum (Converter):
    """
    Converts a value into a string value
    """
    
    #//-------------------------------------------------------//
    
    class __Value (object):
        __slots__ = ('value', 'aliases', 'compare_func')
        
        #//-------------------------------------------------------//
        
        def     __init__(self, value, compare_func ):
            self.value = value
            self.aliases = []
            self.compare_func = compare_func
        
        #//-------------------------------------------------------//
        
        def     get(self):
            return self.value
        
        #//-------------------------------------------------------//
        
        def     __eq__(self, other):
            cmp_func = self.compare_func
            
            for value in [self.value] + self.aliases:
                result = cmp_func( value, other )
                if result == 0:
                    return True
            
            return False
        
        #//-------------------------------------------------------//
        
        def     __ne__(self, other):
            return not self.__eq__(other)
        
        #//-------------------------------------------------------//
        
        def     __cmp__(self, other):
            if self == other:
                return 0
            return self.compare_func( self.value, other )
        
        #//-------------------------------------------------------//
        
        def     addAlias( self, alias ):
            if self != other:
                self.aliases.append( alias )
    
    #//-------------------------------------------------------//
    
    def     __init__(self, type_converter )
        
        self.type_converter = type_converter
        self.allowed_values = {}
        
        def     _convert( value ):
            
        
        convert_func = 
        
        
        Converter.__init__( self, type_converter.base_type, type_converter.compare_func, convert_func )
        
        if comparator is None:
            comparator = cmp
        
        def     _strConverter( value ):
            if value is not None:
                value = str(value)
            else:
                value = str()
        
        if converter is None:
            converter = _strConverter
        else:
            converter = lambda value, converter = converter, _strConverter = _strConverter: converter( _strConverter(value) )
    
    #//-------------------------------------------------------//
    
    def   toString( self, value ):
        return self.convert( value )
    
    def   typeHelp( self, value ):
        return "String"
    
    def   valuesHelp( self, value ):
        return "String"

