from reaper_python import *
from vgmidi import MIDINote, MIDIEvent, MIDITrackData

MAXLEN = 1048567            # Max string length, stolen from CAT.
YES = 6                     # Return values from RPR_MB
NO = 7

def vg_error(message):
    RPR_MB(message, "venuegen", 0)

def vg_log(message):
    RPR_ShowConsoleMsg(message)
    RPR_ShowConsoleMsg('\n')

def vg_verify(message):
    return RPR_MB(message, "venuegen", 4)

def get_reaper_item(title):
    tracks = {}
    for i in range(RPR_CountTracks(0)):
        t = RPR_GetTrack(0, i)
        _, _, _, t_name, _ = RPR_GetSetMediaTrackInfo_String(t, "P_NAME", "", False)
        if len(t_name) > 0:
            tracks[t_name.lower().strip()] = t
    if title not in tracks:
        return None
    icount = RPR_CountTrackMediaItems(tracks[title])
    if icount == 0: return None
    matched_items = []
    for i in range(RPR_CountMediaItems(0)):
        m = RPR_GetMediaItem(0, i)
        if RPR_GetMediaItem_Track(m) == tracks[title]:
            matched_items.append(m)
    if len(matched_items) == 0: return None
    return matched_items[0]

def get_midi_data(item):
    notes_array = []
    notes_pos = 0
    start_midi = 0
    end_midi = 0
    _, _, chunk, _, _ = RPR_GetItemStateChunk(item, "", MAXLEN, False)
    chunk = chunk.strip()
    vars_array = chunk.split('\n')
    i = 0
    while i < len(vars_array):
        note = ""
        if vars_array[i].startswith("E ") or vars_array[i].startswith("e "):
            if start_midi == 0: start_midi = i
            note = vars_array[i].split(" ")
            if len(note) >= 5:
                decval = int(note[3], 16) # MIDI note value
                notes_pos = notes_pos + int(note[1]) # Ticks since last note
                status = int(note[2], 16)
                velocity = int(note[4], 16)
                n = MIDINote(int(note[1]), notes_pos, status, decval, velocity) 
                notes_array.append(n)
        elif vars_array[i].startswith("<X") or vars_array[i].startswith("<x"):
            if start_midi == 0: start_midi = i
            note = vars_array[i].split(" ")
            if len(note) >= 2:
                notes_pos = notes_pos + int(note[1])
                encText = vars_array[i+1]
                status = int(note[2])
                e = MIDIEvent(int(note[1]), notes_pos, status, encText)
                notes_array.append(e)
                i = i + 2
        elif vars_array[i].startswith("POOLEDEVTS"):
            if start_midi == 0: start_midi = i + 1
        else:
            if start_midi != 0 and end_midi == 0: end_midi = i
        i = i + 1
    data = MIDITrackData(chunk, start_midi, end_midi, notes_array)
    return data

def write_midi_data(item, data):
    #vg_log(str(data))
    RPR_SetItemStateChunk(item, str(data), True)
    #vg_log("WRITE MIDI DATA OUTPUT:")
    #vg_log(RPR_SetItemStateChunk(item, str(data), True))
