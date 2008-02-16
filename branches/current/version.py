
import re

#13.10.3077
#8.00v
#4.1.1
#1.6
#8.42n
#5.5.1

def     _parse_version( version ):
    match = re.search(r'[0-9]+[a-zA-Z]*(\.[0-9]+[a-zA-Z]*)*', str( version ) )
    
    if match:
        ver_str = match.group()
        ver = re.findall(r'[0-9]+|[a-zA-Z]+', ver_str )
    else:
        ver_str = ""
        ver = []
    
    return [ ver_str, ver ]

#//---------------------------------------------------------------------------//

class   Version:
    
    def     __init__( self, version ):
        
        self.ver_str, self.ver = _parse_version( version )
    
    #//-------------------------------------------------------//
    
    def     __cmp__( self, other ):
        
        ver1 = self.ver
        len1 = len( ver1 )
        
        ver2 = _parse_version( str(other) )[1]
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
    
    def     __str__( self ):
        
        return self.ver_str
