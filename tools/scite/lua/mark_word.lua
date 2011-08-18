
scite_Command {
   'Mark word|markOccurrences|Alt+h',
   'Unmark words|clearAllOccurrences|Alt+c',
}

local marked_words = {}
local MARKER_COLORS = {0x0000FF, 0x00C000, 0xFF0000, 0xFF00FF, 0xFFFF00, 0x00FFFF }
local MARKER_COUNTS = {}

-- //---------------------------------------------------------------------------//

local function  updateMarkerCounter( mark, marker_number )
    current_mark_counter = MARKER_COUNTS[ marker_number ] or 0
    if mark then
      current_mark_counter = current_mark_counter + 1
    else
      current_mark_counter = current_mark_counter - 1
    end
    
    MARKER_COUNTS[ marker_number ] = current_mark_counter
end

-- //---------------------------------------------------------------------------//

local function  clearMarkerCounters()
    for marker_number, color in ipairs(MARKER_COLORS) do
      MARKER_COUNTS[marker_number] = 0
    end
end

-- //---------------------------------------------------------------------------//

local function  getMarkerNumber()
    local min_marker_number = 1
    local min_counter = nil
    
    for marker_number, counter in ipairs(MARKER_COUNTS) do
        if (min_counter == nil) or (min_counter > counter) then
          min_counter = counter
          min_marker_number = marker_number
        end
    end
    
    return min_marker_number
end

-- //---------------------------------------------------------------------------//

local isMarkStylesInitialized = false
local function initMarkStyles()
    if isMarkStylesInitialized then
      return
    end
    
    isMarkStylesInitialized = true
    
    for style_number, color in ipairs(MARKER_COLORS) do
        editor.IndicStyle[ style_number ] = INDIC_ROUNDBOX
        editor.IndicFore[ style_number ] = color
        editor.IndicAlpha[ style_number ] = 90
    end
    
    clearMarkerCounters()
end

-- //---------------------------------------------------------------------------//

local function markText(start, length, mark, marker_number )
    
    local current_mark_number = scite.SendEditor(SCI_GETINDICATORCURRENT)
    scite.SendEditor(SCI_SETINDICATORCURRENT, marker_number )

    if mark then
        scite.SendEditor(SCI_INDICATORFILLRANGE, start, length )
    else
        scite.SendEditor(SCI_INDICATORCLEARRANGE, start, length )
    end
    
    scite.SendEditor(SCI_SETINDICATORCURRENT, current_mark_number)
end

-- //---------------------------------------------------------------------------//

local function markUnmarkWord( word, mark )
    
    initMarkStyles()
    
    local marker_number = marked_words[word]
    
    if mark then
      if marker_number == nil then
        marker_number = getMarkerNumber()
        marked_words[word] = marker_number
      end
    else
      if marker_number == nil then
        return
      end
      
      marked_words[word] = nil
    end
    
    local flags = SCFIND_WHOLEWORD + SCFIND_MATCHCASE
    local s,e = editor:findtext(word,flags,0)
    while s do
        updateMarkerCounter( mark, marker_number )
        markText( s, e - s, mark, marker_number )
        s,e = editor:findtext(word,flags,e+1)
    end
end

-- //---------------------------------------------------------------------------//

local function markUnmakrAll( mark )
    
    for word,marker_number in pairs(marked_words) do
        markUnmarkWord( word, mark )
    end
end

-- //---------------------------------------------------------------------------//

local function clearIndicators()
    for marker_number, color in ipairs(MARKER_COLORS) do
      markText( 0, editor.Length, false, marker_number )
    end
end

-- //---------------------------------------------------------------------------//

local function GetCurrentWord()
    if editor.SelectionStart ~= editor.SelectionEnd then
        return editor:GetSelText()
    end
    
    local current_pos = editor.CurrentPos
    return editor:textrange( editor:WordStartPosition(current_pos, true),
                             editor:WordEndPosition(current_pos, true) )
end

-- //---------------------------------------------------------------------------//

function markOccurrences()
    word = GetCurrentWord()
    markUnmarkWord( word, marked_words[word] == nil )
end

-- //---------------------------------------------------------------------------//

function clearAllOccurrences()
    marked_words = {}
    clearMarkerCounters()
    clearIndicators()
end

function markAllOccurrences()
    clearIndicators()
    clearMarkerCounters()
    markUnmakrAll( true )
end

scite_OnSwitchFile( markAllOccurrences )
scite_OnOpen( markAllOccurrences )
