import sys
import os

def findStr( path, search_str, files_ext ):
    
    search_str = search_str.lower()
    
    path = os.path.abspath(path)
    
    for root, dirs, files in os.walk(path):
        
        # root = os.path.abspath(root)
        
        for d in dirs:
            if d.startswith('.') or (d.lower() in ['output', '3rdparty']):
                dirs.remove(d)
        
        for f in files:
            fname, fext = os.path.splitext(f)
            
            if fext[1:].isdigit():
                fname, fext = os.path.splitext(fname)
            
            fext = fext.lower()
            
            if fext in files_ext:
                ln = 1
                fpath = os.path.normpath(os.path.join(root, f))
                try:
                    for l in open(fpath):
                        if l.lower().find(search_str) != -1:
                            sys.stdout.write( fpath + ':' + str(ln) + ':   ' + l )
                        ln += 1
                except:
                    print "fpath:", fpath

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        sys.stderr.write('Search string is not specified.\n')
        exit(1)
    
    files_ext = set( ('.c', '.cpp', '.cxx', '.h', '.hpp', '.hxx', '.xml', '.py', '.pl'
                      '.mak', '.mc', '.msg', '.mof', '.log'
                      '') )
    
    if (len(sys.argv) > 2):
        path = sys.argv[2]
    else:
        path = '.'
    
    findStr(path, sys.argv[1], files_ext )
