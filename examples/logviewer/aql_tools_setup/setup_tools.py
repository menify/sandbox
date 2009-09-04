import aql.setup

def     setup_tools( options, os_env ):
    
    if_cc_name = options.If().cc_name.ne(None).cc_name
    
    if_cc_name['gcc'].tools += 'aql_tool_gcc'
    if_cc_name['msvc'].tools += ['msvc', 'mslink', 'mslib']
    
    options.If().cc_name.eq(None).tools += 'aql_tool_default_cc'

#//---------------------------------------------------------------------------//

aql.setup.AddSiteSetup( setup_tools )
