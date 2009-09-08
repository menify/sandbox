from aql.setup import siteSetup

@siteSetup
def     setup_tools( options, os_env ):
    
    if_cc_name = options.If().cc_name.ne(None).cc_name
    
    if_cc_name['gcc'].tools += 'aql_tool_gcc'
    #~ if_cc_name['msvc'].tools += ['msvc', 'mslink', 'mslib']
    if_cc_name['msvc'].tools += 'aql_tool_msvc'
    options.If().lint.ne('off').tools += 'aql_tool_flexelint'
    options.If().cc_name.eq(None).tools += 'aql_tool_default_cc'
