import aql.setup

def     setup_tools( options, os_env ):
    
    if_cc_name = options.If().cc_name
    
    if_cc_name['gcc'].tools += 'aql_tool_gcc'
    if_cc_name['msvc'].tools += 'aql_tool_msvc'

#//---------------------------------------------------------------------------//

aql.setup.AddSiteSetup( setup_tools )
