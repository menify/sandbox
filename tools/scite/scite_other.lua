-- scite_other.lua
-- This uses the scite_other.dll to provide the following functions
-- PerformOther(verb,arg)
-- Perform(verb,arg)
--  (executes above commands in _this_ instance of SciTE)
-- Execute(cmd)
--  (quiet replacement for os.execute - no more flashing black boxes!)
-- OpenOther(file,line)
--  (open a file in another instance of ScITE, optionally specifying the line)
-- Command(id,other)
--  (execute a SciTE menu commmand)
-- 
-- Steve Donovan, 2004

local TEMP_FILE_IN = "/scite_other_temp1"
local TEMP_FILE_OUT = "/scite_other_temp2"
local our_window = 0
local fn = package.loadlib(props['SciteUserHome']..'/scite_other.dll','scite_other')
if not fn then print 'cannot load scite_other.dll!!' end

function Perform(verb,arg,other)
  local f = io.open(TEMP_FILE_IN,'w')
  if not arg then 
     arg = ''
  else   
   -- exec is a special verb _not_ handled by the Director interface,
   -- which otherwise requires its input to be slashified. 
    if verb ~= 'exec' then 
      arg = string.gsub(arg,'\\','\\\\')
    end
  end
  local cmd = 1
  if other then cmd = 0 end
  f:write(verb,':',arg,'\n')
  f:write(cmd,' ',our_window,'\n')
  f:close()
  fn()
  if verb ~= 'exec' then
    f = io.open(TEMP_FILE_OUT,'r')
    local n = f:read('*n')
    f:read()
    if n == 1 then
      our_window = f:read()
    end
  end
end

function PerformOther(verb,arg)
  Perform(verb,arg,true)
end

function Execute(cmd)
  Perform('exec',cmd)
end

function OpenOther(file,line)  
  PerformOther('open',file)
  if line then 
    PerformOther('goto',line)
  end
end

-- extracted from SciTE.h
local CommandMap = {
 IDM_TOOLS = 1100,
 IDM_NEW = 101,
 IDM_OPENSELECTED = 103,
 IDM_REVERT = 104,
 IDM_SAVE = 106,
 IDM_PRINT = 131,
 IDM_ENCODING_DEFAULT = 150,
 IDM_ENCODING_UCS2BE = 151,
 IDM_ENCODING_UCS2LE = 152,
 IDM_ENCODING_UTF8 = 153,
 IDM_ENCODING_UCOOKIE = 154,
 IDM_FINDNEXT = 211,
 IDM_FINDNEXTBACK = 212,
 IDM_FINDNEXTSEL = 213,
 IDM_FINDNEXTBACKSEL = 214,
 IDM_BOOKMARK_NEXT = 221,
 IDM_BOOKMARK_TOGGLE = 222,
 IDM_BOOKMARK_PREV = 223,
 IDM_BOOKMARK_CLEARALL = 224,
 IDM_BOOKMARK_NEXT_SELECT = 225,
 IDM_BOOKMARK_PREV_SELECT = 226,
 IDM_MATCHBRACE = 230,
 IDM_SELECTTOBRACE = 231,
 IDM_SHOWCALLTIP = 232,
 IDM_COMPLETE = 233,
 IDM_COMPLETEWORD = 234,
 IDM_EXPAND = 235,
 IDM_TOGGLE_FOLDALL = 236,
 IDM_UPRCASE = 240,
 IDM_LWRCASE = 241,
 IDM_ABBREV = 242,
 IDM_BLOCK_COMMENT = 243,
 IDM_STREAM_COMMENT = 244,
 IDM_COPYASRTF = 245,
 IDM_BOX_COMMENT = 246,
 IDM_INS_ABBREV = 247,
 IDM_JOIN = 248,
 IDM_SPLIT = 249,
 IDM_INCSEARCH = 252,
 IDM_ENTERSELECTION = 256,
 IDM_COMPILE = 301,
 IDM_BUILD = 302,
 IDM_GO = 303,
 IDM_STOPEXECUTE = 304,
 IDM_FINISHEDEXECUTE = 305,
 IDM_NEXTMSG = 306,
 IDM_PREVMSG = 307, 
 IDM_SPLITVERTICAL = 401,
 IDM_VIEWSPACE = 402,
 IDM_VIEWEOL = 403,
 IDM_VIEWGUIDES = 404,
 IDM_SELMARGIN = 405,
 IDM_FOLDMARGIN = 406,
 IDM_LINENUMBERMARGIN = 407,
 IDM_VIEWTOOLBAR = 408,
 IDM_TOGGLEOUTPUT = 409,
 IDM_VIEWTABBAR = 410,
 IDM_VIEWSTATUSBAR = 411,
 IDM_OPENFILESHERE = 413,
 IDM_WRAP = 414,
 IDM_WRAPOUTPUT = 415,
 IDM_READONLY = 416,
 IDM_CLEAROUTPUT = 420,
 IDM_SWITCHPANE = 421,
 IDM_EOL_CRLF = 430,
 IDM_EOL_CR = 431,
 IDM_EOL_LF = 432,
 IDM_EOL_CONVERT = 433,
 IDM_MONOFONT = 450,
 IDM_OPENLOCALPROPERTIES = 460,
 IDM_OPENUSERPROPERTIES = 461,
 IDM_OPENGLOBALPROPERTIES = 462,
 IDM_OPENABBREVPROPERTIES = 463,
 IDM_OPENLUAEXTERNALFILE = 464,
 IDM_SAVEALL = 504,
 IDM_FULLSCREEN = 961,
}

function Command(id,other)
  if type(id) == 'string' then id = CommandMap[id] end
  if id then 
    Perform('menucommand',id,other)
  end
end



