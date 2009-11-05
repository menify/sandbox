

class   Converter:
    """
    A base class to convert a value into base value (string, int, bool, node and etc.)
    """
    
    #//-------------------------------------------------------//
    
    def   __init__(self, base_type, comparator = None, converter = None, validator = None )
        
        class BaseType (base_type):
            pass
        
        self.base_type = BaseType
        self.comparator = comparator
        self.converter = converter
        self.validator = validator
    
    #//-------------------------------------------------------//
    
    def   convert( self, value):
        raise TypeError("Abstract method. Should be implemented in child classes")
    
    #//-------------------------------------------------------//
    
    def   validate( self, value, isinstance = isinstance ):
        try:
            value = self.convert( value )
        except:
            return False
        
        return (self.validator is None) or self.validator( value )
    
    #//-------------------------------------------------------//
    
    def   compare( self, value1, value2 ):
        value1 = self.convert( value1 )
        value2 = self.convert( value2 )
        
        if self.comparator is not None:
            return self.comparator( value1, value2 )
        
        return cmp(value1, value2)
    
    #//-------------------------------------------------------//
    
    def   toString( self, value ):
        raise TypeError("Abstract method. Should be implemented in child classes")
    
    def   typeHelp( self, value ):
        raise TypeError("Abstract method. Should be implemented in child classes")
    
    def   valuesHelp( self, value ):
        raise TypeError("Abstract method. Should be implemented in child classes")

#//===========================================================================//

class   ConverterString:
    """
    Converts a value into base value (string, int, bool, node)
    """
    
    class __ConvertedValue (str):
        pass
    
    #//-------------------------------------------------------//
    
    def   convert( self, value, isinstance = isinstance ):
        if isinstance( value, __ConvertedValue ):
            return value
      
        if value is not None:
            value = str(value)
        else:
            value = str()
      
        if self.converter is not None:
            value = self.converter( value )
      
        converted_value = __ConvertedValue( value )
      
        if not self.validate( converted_value ):
            TypeError("")
    
    #//-------------------------------------------------------//
    
    def   toString( self, value ):
        return self.convert( value )

