
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
            ver = re.findall(r'[0-9]+|[a-zA-Z]+', ver_str )
        else:
            ver_str = ''
            ver = []
        
        self = super(Version, cls).__new__(cls, ver_str )
        self.ver = ver
        
        print "Version.__new__:", id(self)
        
        return self
    
    #//-------------------------------------------------------//
    
    def     __cmp__( self, other ):
        
        ver1 = self.ver
        len1 = len( ver1 )
        
        ver2 = Version( other ).ver
        len2 = len( ver2 )
        
        min_len = min( len1, len2 )
        if min_len == 0:
            return len1 - len2
        
        for i in xrange( 0, min_len ):
            
            v1 = ver1[i]
            v2 = ver2[i]
            
            if (v1.isdigit()) and (v2.isdigit()):
                v1 = int(v1)
                v2 = int(v2)
            
            if v1 < v2:
                return -1
            if v1 > v2:
                return 1
        
        return 0
    
    #//-------------------------------------------------------//
    
    def __lt__( self, other):       return self.__cmp__(other) < 0
    def __le__( self, other):       return self.__cmp__(other) <= 0
    def __eq__( self, other):       return self.__cmp__(other) == 0
    def __ne__( self, other):       return self.__cmp__(other) != 0
    def __gt__( self, other):       return self.__cmp__(other) > 0
    def __ge__( self, other):       return self.__cmp__(other) >= 0


#//---------------------------------------------------------------------------//


class   ConverterEnum (object):
    
    __slots__ = ('values_map')
    
    def     __init__( self ):
        self.values_map = {}
    
    def     __call__( self, value ):
        
        try:
            while True:
                value = self.values_dict[ value ]
                if value is None:
                    break;
        except:
            raise TypeError("Invalid value: %s " % value )
        
        
        mapped_values = []
        
        for v in toSequence( values ):
            
            try:
                v = str(v).lower()
                alias = values_dict[ v ]
            
            except (AttributeError, KeyError):
                
                if self.shared_data['all_key'] == v:
                    alias = self.AllowedValues()
                
                else:
                    return None
            
            if alias is None:
                mapped_values.append( v )
            else:
                mapped_values += alias
        
        return mapped_values
    
    #//=======================================================//
    
    def     _convert_value( self, val ):
        
        values = self.__map_values( val )
        
        if not values:
            _Error( "Invalid value: '%s', type: %s" % (val, type(val)) )
        
        if len( values ) == 1:
            return values[0]
        
        return values
    
    #//=======================================================//
    
    def     AddValues( self, values, toSequence = utils.toSequence ):
        values_dict = self.shared_data['values_dict']
        
        for v in toSequence( values ):
            
            try:
                v = v.lower()
            except AttributeError:
                _Error( "Invalid value: '%s', type: %s" % (val, type(val)) )
            
            if self.__map_values( v ):
                _Error( "Can't change an existing value: %s" % (v) )
            
            values_dict[ v ] = None
    
    #//=======================================================//
    
    def     AddAlias( self, alias, values, isSequence = utils.isSequence ):
        
        if self.__map_values( alias ):
            _Error( "Can't change an existing value: %s" % (alias) )
        
        mapped_values = self.__map_values( values )
        if not mapped_values:
            _Error( "Invalid value(s): %s" % (values) )
        
        if (not self.shared_data['is_list']) and (len( mapped_values ) > 1):
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
                v = v + ' (or ' + ", ".join( a ) + ')'
            
            allowed_values.append( v )
        
        allowed_values = map( lambda v: '- ' + v, allowed_values )
        allowed_values_str = '\n'.join( allowed_values )
        
        if len(allowed_values) > 1:
            allowed_values_str = '\n' + allowed_values_str
        
        return allowed_values_str
    
    #//-------------------------------------------------------//
    
    def     AllowedValuesHelp( self ):
        if self.shared_data['is_list']:
            return 'List of values: ' + self.AllowedValuesStr()
        
        return 'A value: ' + self.AllowedValuesStr()


#//---------------------------------------------------------------------------//

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
        print "cmp:", a, b
        return cmp( a[0], b[0] )
    
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

