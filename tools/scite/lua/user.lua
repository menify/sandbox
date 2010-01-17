-- User's extentions

if scite_Command then -- extman is present!
    scite_Command {
       'Select word|select_word|Shift+Enter',
       'Convert to LF|convert_to_lf|Alt+F',
       'Hexify Selection|HexifySelection|',
       'Tabs to Spaces|TabToSpace|Alt+J',
       'Invert value|ToggleBinaryValue|Alt+R',
    }
end

function select_word()
    local cur_pos = editor.CurrentPos
    local word_start = editor:WordStartPosition( cur_pos, true )
    local word_end = editor:WordEndPosition( cur_pos, true )
    
    editor:SetSel( word_start, word_end )
end


function convert_to_lf()
    IDM_EOL_LF = 432
    IDM_EOL_CONVERT = 433
    IDM_SAVE = 106
    
    scite.MenuCommand(IDM_EOL_LF)
    scite.MenuCommand(IDM_EOL_CONVERT)
    scite.MenuCommand(IDM_SAVE)
end


-- Convert a string to a string of hex escapes
function Hexify(s) 
  local hexits = ""
  for i = 1, string.len(s) do
    hexits = hexits .. string.format("\\x%2x", string.byte(s, i))
  end
  return hexits
end

-- Convert the selection to hex escaped form
function HexifySelection()
  editor:ReplaceSel(Hexify(editor:GetSelText()))
end


-----------------------------------------------------------------------
-- Tabs to spaces (EditPad-style) for SciTE (self-contained)
-- Kein-Hong Man <khman@users.sf.net> 20040727
-- This program is hereby placed into PUBLIC DOMAIN
-----------------------------------------------------------------------
-- Best installed as a shortcut key, e.g. Ctrl-1 with the following in
-- your user properties file, usually SciTEUser.properties:
--     command.name.1.*=Tabs to Spaces
--     command.subsystem.1.*=3
--     command.1.*=TabToSpace
--     command.save.before.1.*=2
-- This Lua function itself should be in SciTEStartup.lua, assuming it
-- is properly set up. Consult SciTEDoc.html if you are unsure of what
-- to do. You can also keep it in a separate file and load it using:
--     require(props["SciteUserHome"].."/SciTE_TabSpace.lua")
-- Tested on SciTE 1.61+ (CVS 20040718) on Win98SE. Be careful when
-- tweaking it, you *may* be able to crash SciTE. You have been warned!
-----------------------------------------------------------------------
-- This is useful if you often copy text over to a word processor for
-- printing. Word processors have tabs based on physical lengths, so
-- indentation of source code would usually start to run. The current
-- tab width can be overridden using a global property:
--     ext.lua.tabtospace.tabsize=8
-----------------------------------------------------------------------
TabToSpace = function()
  -- get override or editor's current tab size
  local tab = tonumber(props["ext.lua.tabtospace.tabsize"])
  if not tab then tab = editor.TabWidth end
  editor:BeginUndoAction()
  for ln = 0, editor.LineCount - 1 do
    local lbeg = editor:PositionFromLine(ln)
    local lend = editor.LineEndPosition[ln]
    local text = editor:textrange(lbeg, lend)
    local changed = false
    while true do
      local x, y = string.find(text, "\t", 1, 1)
      if x then -- found tab, replace
        local z = x - 1 + tab
        y = z - math.mod(z, tab) + 1 -- tab stop position
        text = string.sub(text, 1, x - 1) ..
               string.rep(" ", y - x) ..
               string.sub(text, x + 1)
        changed = true
      else -- no more tabs
        break
      end
    end--while
    if changed then
      editor.TargetStart = lbeg
      editor.TargetEnd = lend
      editor:ReplaceTarget(text)
    end
  end--for
  editor:EndUndoAction()
end

-- toggle the word under the cursor.
function ToggleBinaryValue()
 local cur_pos = editor.CurrentPos
 local word_start = editor:WordStartPosition( cur_pos, true )
 local word_end = editor:WordEndPosition( cur_pos, true )
 editor:SetSel( word_start, word_end )
 
 local Word = editor:GetSelText()
 
 if Word == "FALSE" then editor:ReplaceSel("TRUE") end
 if Word == "TRUE" then editor:ReplaceSel("FALSE") end
 if Word == "false" then editor:ReplaceSel("true") end
 if Word == "true" then editor:ReplaceSel("false") end
 if Word == "False" then editor:ReplaceSel("True") end
 if Word == "True" then editor:ReplaceSel("False") end
 if Word == "YES" then editor:ReplaceSel("NO") end
 if Word == "NO" then editor:ReplaceSel("YES") end
 if Word == "yes" then editor:ReplaceSel("no") end
 if Word == "no" then editor:ReplaceSel("yes") end
 if Word == "0" then editor:ReplaceSel("1") end
 if Word == "1" then editor:ReplaceSel("0") end
 if Word == "on" then editor:ReplaceSel("off") end
 if Word == "off" then editor:ReplaceSel("on") end
 if Word == "ON" then editor:ReplaceSel("OFF") end
 if Word == "OFF" then editor:ReplaceSel("ON") end
 
 if Word == "SYN_TRUE" then editor:ReplaceSel("SYN_FALSE") end
 if Word == "SYN_FALSE" then editor:ReplaceSel("SYN_TRUE") end
 
 if Word == "SYN_SUCCESS" then editor:ReplaceSel("SYN_FAIL") end
 if Word == "SYN_FAIL" then editor:ReplaceSel("SYN_SUCCESS") end
 
 editor:GotoPos(cur_pos)
end
