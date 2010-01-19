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
        self.__version = ver
        
        return self
    
    #//-------------------------------------------------------//
    
    def     __cmp__( self, other ):
        
        ver1 = self.__version
        len1 = len( ver1 )
        
        ver2 = Version( other ).__version
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
