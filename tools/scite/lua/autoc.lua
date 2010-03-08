local IGNORE_CASE = false
-- Number of chars to type before the autocomplete list appears:
local MIN_PREFIX_LEN = 2
-- Length of shortest word to add to the autocomplete list
local MIN_IDENTIFIER_LEN = MIN_PREFIX_LEN + 1
-- A list of string patterns for finding suggestions for the autocomplete menu.
local IDENTIFIER_PATTERNS = {"[%a_][%w_]+", "[%a_][%w_.]*[%w_]", "[%a_][%w_-]*[%w_]"}

local names = {}
local notempty = next

if IGNORE_CASE then
    normalize = string.lower
else
    normalize = function(word) return word end
end


function buildNames()
    names = {}
    local text = editor:GetText()
    for i, pattern in ipairs(IDENTIFIER_PATTERNS) do
        for word in string.gmatch(text, pattern) do
            if string.len(word) >= MIN_IDENTIFIER_LEN then
                names[word] = normalize(word)
            end
        end
    end
end


function handleChar()
--~     if not editor:AutoCActive() then
        editor.AutoCIgnoreCase = IGNORE_CASE
        local pos = editor.CurrentPos
        local startPos = editor:WordStartPosition(pos, true)
        local len = pos - startPos
        if len >= MIN_PREFIX_LEN then
            local prefix = normalize( editor:textrange(startPos, pos) )
            if string.find( prefix, "%w" ) == nil then return end
            local menuItems = {}
            for name, normname in pairs(names) do
                if prefix ~= normname and string.sub(normname, 1, len) == prefix then
                    table.insert(menuItems, name)
                end
            end
            if notempty(menuItems) then
                table.sort(menuItems)
                scite.SendEditor( SCI_AUTOCSETSEPARATOR, 10 )
                scite.SendEditor( SCI_AUTOCSETMAXHEIGHT, 10 )
--~                 scite.SendEditor( SCI_AUTOCSETDROPRESTOFWORD, 1 )
                scite.SendEditor( SCI_AUTOCSETAUTOHIDE, 1 )
                editor:AutoCShow(len, table.concat(menuItems, "\n") )
            else
              editor:AutoCCancel()
            end
        end
--~     end
end

scite_OnChar( handleChar )
scite_OnSave( buildNames )
scite_OnSwitchFile( buildNames )
scite_OnOpen( buildNames )


