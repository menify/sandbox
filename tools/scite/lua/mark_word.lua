
scite_Command {
   'Mark word|markOccurrences|Alt+H',
   'Unmark words|clearOccurrences|Alt+C',
}

local marked_words = {}
local MARKER_STYLE_NUMER = 0

-- //---------------------------------------------------------------------------//

local isMarkStylesInitialized = false
local function initMarkStyles()
    if not isMarkStylesInitialized then
        editor.IndicStyle[MARKER_STYLE_NUMER] = INDIC_ROUNDBOX
        editor.IndicFore[MARKER_STYLE_NUMER] = 255
        editor.IndicAlpha[MARKER_STYLE_NUMER] = 30
        isMarkStylesInitialized = true
    end
end

scite_OnOpen( initMarkStyles )

-- //---------------------------------------------------------------------------//

function markText(start, length, mark )
    local current_mark_number = scite.SendEditor(SCI_GETINDICATORCURRENT)
    scite.SendEditor(SCI_SETINDICATORCURRENT, MARKER_STYLE_NUMER )
    if mark then
        scite.SendEditor(SCI_INDICATORFILLRANGE, start, length )
    else
        scite.SendEditor(SCI_INDICATORCLEARRANGE, start, length )
    end
    scite.SendEditor(SCI_SETINDICATORCURRENT, current_mark_number)
end

-- //---------------------------------------------------------------------------//

function markUnmarkWord( word, mark )
    marked_words[word] = mark or nil
    
    local flags = SCFIND_WHOLEWORD
    local s,e = editor:findtext(word,flags,0)
    while s do
        markText( s, e - s, mark )
        s,e = editor:findtext(word,flags,e+1)
    end
end

-- //---------------------------------------------------------------------------//

function clearOccurrences()
    markText( 0, editor.Length, false )
    marked_words = {}
end

-- //---------------------------------------------------------------------------//

function markAllOccurrences()
    markText( 0, editor.Length, false )
    for word,mark in pairs(marked_words) do
        if mark ~= nil then markUnmarkWord( word, true ) end
    end
end

scite_OnSwitchFile( markAllOccurrences )

-- //---------------------------------------------------------------------------//

function markOccurrences()
    word = GetCurrentWord()
    markUnmarkWord( word, marked_words[word] == nil )
end

-- //---------------------------------------------------------------------------//

function GetCurrentWord()
    if editor.SelectionStart ~= editor.SelectionEnd then
        return editor:GetSelText()
    end
    
    local current_pos = editor.CurrentPos
    return editor:textrange( editor:WordStartPosition(current_pos, true),
                             editor:WordEndPosition(current_pos, true) )
end
