

scite_Command {
   'Mark word|markOccurrences|Alt+H',
   'Unmark words|clearOccurrences|Alt+C',
}

local marked_words = {}
local INDICATOR_NUMBER = 0

function clearOccurrences()
    scite.SendEditor(SCI_INDICATORCLEARRANGE, INDICATOR_NUMBER, editor.Length)
    marked_words = {}
end

function markAllOccurrences()
    scite.SendEditor(SCI_INDICATORCLEARRANGE, INDICATOR_NUMBER, editor.Length)
    for word,mark in pairs(marked_words) do
        if mark ~= nil then markUnmarkWord( word, true ) end
    end
end

function markOccurrences()
    word = GetCurrentWord()
    markUnmarkWord( word, marked_words[word] == nil )
end

function markUnmarkWord( word, mark )
    local indop = SCI_INDICATORFILLRANGE
    
    if mark then
        marked_words[word] = true
        
        scite.SendEditor(SCI_INDICSETSTYLE, INDICATOR_NUMBER, INDIC_ROUNDBOX)
        scite.SendEditor(SCI_INDICSETFORE, INDICATOR_NUMBER, 255)
    else
        marked_words[word] = nil
        indop = SCI_INDICATORCLEARRANGE
    end
    
    local flags = SCFIND_WHOLEWORD
    local s,e = editor:findtext(word,flags,0)
    while s do
        scite.SendEditor(indop, s, e - s)
        s,e = editor:findtext(word,flags,e+1)
    end
end

function isWordChar(char)
    local strChar = string.char(char)
    local beginIndex = string.find(strChar, '%w')
    if beginIndex ~= nil then
        return true
    end
    if strChar == '_' or strChar == '$' then
        return true
    end
    
    return false
end

function GetCurrentWord()
    local beginPos = editor.CurrentPos
    local endPos = beginPos
    if editor.SelectionStart ~= editor.SelectionEnd then
        return editor:GetSelText()
    end
    while isWordChar(editor.CharAt[beginPos-1]) do
        beginPos = beginPos - 1
    end
    while isWordChar(editor.CharAt[endPos]) do
        endPos = endPos + 1
    end
    return editor:textrange(beginPos,endPos)
end

scite_OnSwitchFile( markAllOccurrences )
