
def     GenerateOptionsHelp( options, detailed_help ):
    
    prefix = "  "
    
    help = "\nOptions to control builds.\n" \
           "The values can be overridden via command line or a config file.\n" \
           "Like this: scons optimization=speed debug_info=1 cc_name=gcc\n" \
           "Or within your build scripts or config files.\n"
    help += '=' * max( map(len, help.split('\n')) ) + '\n'
    
    sorted_options = []
    
    max_name_len = 0
    
    for id, op_names in options.__dict__['__ids_dict'].iteritems():
        
        op = op_names[0]
        
        if op.shared_data['help'] is None:
            continue
        
        names = op_names[1:]
        
        max_name_len = max( [ max_name_len ] + map(len, names) )
        
        sorted_options.append( (op, names) )
    
    def     _cmp_options( op_names1, op_names2 ):
        
        op1,names1 = op_names1
        op2,names2 = op_names2
        
        g1 = op1.shared_data['group']
        g2 = op2.shared_data['group']
        
        if g1 == 'User' and g2 != 'User':
            return 1
        
        if g1 != 'User' and g2 == 'User':
            return -1
        
        result = cmp( g1, g2 )
        if result == 0:
            result = cmp( names1[0].lower(), names2[0].lower() )
        
        return result
    
    #~ sorted_options.sort( lambda x,y: cmp(x[1][0].lower(), y[1][0].lower()) )
    sorted_options.sort( _cmp_options )
    
    group = ''
    
    for n in sorted_options:
        
        op    = n[0]
        names = n[1]
        
        g = op.shared_data['group']
        if g != group:
            group = g
            if help[-1] != '\n': help += '\n'
            help += '\n*** ' + group + ' options ***:\n\n'
        
        else:
            if help[-1] != '\n': help += '\n'
        
        if len(names) > 1:
            if not help.endswith('\n\n'):
                help += '\n'
        
        for name in names[:-1]:
            help += prefix + name + ':'
            help += '\n'
        
        name = names[-1]
        
        line = prefix + name + ':'
        
        line += ' ' * ((max_name_len - len(name)) + 2)
        #~ help += line + op.AllowedValuesStr()
        #~ help += '\n%s%s' % ( ' ' * len(line), op.shared_data['help'] )
        help += line + op.shared_data['help']
        
        if detailed_help:
            help += '\n' + ' ' * len(line) + 'Type: '
            #~ if op.shared_data['is_list']:   help += 'List. '
            help += op.AllowedValuesHelp()
        
        help += '\n'
        
        #~ help += str(op.__class__.__name__)
        
        if detailed_help or (len(names) > 1): help += '\n'
    
    return help
