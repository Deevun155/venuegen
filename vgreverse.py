# Functions for event->note mapping.

from vgreaper import *
from vgmidi import (
        MIDI_ON, MIDI_OFF, MIDIEvent, MIDINote, add_note, remove_notes, remove_events
)

from vgprocess import (
        DIRECTED, DIRECTED_FREEBIES, CAMERA, LIGHTS_SINGLE, LIGHTING, POSTPROCS, 
        dict_merge, reverse_dict
)

SINGLE_LEN = 480 // (16 // 4) # 16th note

def verify_overwrite(MIDIdata, name):
    r = YES
    existing_notes = False
    #for note in MIDIdata.notes:
        #if isinstance(note, MIDINote):
            #existing_notes = True
            #break

    #if existing_notes:
        #r = vg_verify("Notes found in \"%s\" track. Delete and replace with pulled venue?" % name)
    return r

def pull_single_instance(data_src, data_dst, map_range):
    #vg_log(map_range)
    #vg_log(data_dst)
    for note in data_src.notes:
        #vg_log(note)
        #vg_log("Is it the instance of the thing?")
        #vg_log(isinstance(note, MIDIEvent))
        #vg_log("Is it the thing in the other thing?")
        #vg_log(note.text in map_range)
        #vg_log(note.text.decode("utf-8"))
        if isinstance(note, MIDIEvent) and note.text in map_range:
            #vg_log(note.text.decode("utf-8"))
            pitch = map_range[note.text]
            #vg_log(pitch)
            add_note(data_dst, note.apos, MIDI_ON, pitch, 64)
            add_note(data_dst, note.apos + SINGLE_LEN, MIDI_OFF, pitch, 0)
    #vg_log(data_dst)

def pull_faded_instance(data_src, data_dst, map_range):
    valid_notes = []
    for note in data_src.notes:
        if isinstance(note, MIDIEvent) and note.text in map_range:
            valid_notes.append(note)

    if len(valid_notes) == 0: return

    pitch = map_range[valid_notes[0].text]
    add_note(data_dst, valid_notes[0].apos, MIDI_ON, pitch, 64)

    event_active = True
    for i in range(1, len(valid_notes)):
        note = valid_notes[i]
        pitch = map_range[note.text]

        if valid_notes[i].text == valid_notes[i-1].text and event_active:
            add_note(data_dst, note.apos, MIDI_OFF, pitch, 0)
            event_active = False
        elif valid_notes[i].text == valid_notes[i-1].text and not event_active:
            add_note(data_dst, note.apos, MIDI_ON, pitch, 64)
            event_active = True
            if i == len(valid_notes) - 1:
                add_note(data_dst, note.apos + SINGLE_LEN, MIDI_OFF, pitch, 0)
        elif valid_notes[i].text != valid_notes[i-1].text and event_active:
            last_pitch = map_range[valid_notes[i-1].text]
            add_note(data_dst, note.apos, MIDI_OFF, last_pitch, 0)
            add_note(data_dst, note.apos, MIDI_ON, pitch, 64)
            if i == len(valid_notes) - 1:
                add_note(data_dst, note.apos + SINGLE_LEN, MIDI_OFF, pitch, 0)
        elif valid_notes[i].text != valid_notes[i-1].text and not event_active:
            add_note(data_dst, note.apos, MIDI_ON, pitch, 64)
            event_active = True
            if i == len(valid_notes) - 1:
                add_note(data_dst, note.apos + SINGLE_LEN, MIDI_OFF, pitch, 0)

def pull_camera_from_venue():
    cam_item = get_reaper_item("camera")
    if cam_item is None: 
        vg_error("Could not find the \"CAMERA\" track.")
        return 

    venue_item = get_reaper_item("venue")
    if venue_item is None: 
        vg_error("Could not find the \"VENUE\" track.")
        return

    single_cam_range = reverse_dict(dict_merge((CAMERA, DIRECTED)))
    
    #vg_log(single_cam_range)
    cam_data = get_midi_data(cam_item)
    #vg_log(cam_data.midi_start)
    #vg_log("CAM BEFORE")
    #vg_log(cam_data)
    venue_data = get_midi_data(venue_item)
    #vg_log(venue_data)

    if verify_overwrite(cam_data, "CAMERA") != YES:
        return

    remove_events(cam_data)
    remove_notes(cam_data)
    #vg_log("CAM AFTER")
    #vg_log(cam_data)
    #vg_log("VENUE")
    #vg_log(venue_data)
    #vg_log(venue_data.midi_start)

    pull_single_instance(venue_data, cam_data, single_cam_range)

    for cut, note in reverse_dict(DIRECTED_FREEBIES).items():
        pull_faded_instance(venue_data, cam_data, { cut: note })

    write_midi_data(cam_item, cam_data)
    #vg_log("THIS IS CAM DATA")
    #vg_log(cam_data)

def pull_lighting_from_venue():
    #vg_log("it got called")
    light_item = get_reaper_item("lighting")
    if light_item is None:
        vg_error("Could not find the \"LIGHTING\" track.")
        return

    venue_item = get_reaper_item("venue")
    if venue_item is None: 
        vg_error("Could not find the \"VENUE\" track.")
        return
    #vg_log(light_item)
    #vg_log(venue_item)
    single_light_range = reverse_dict(LIGHTS_SINGLE)
    faded_lights_range = reverse_dict(LIGHTING)
    faded_procs_range = reverse_dict(POSTPROCS)


    light_data = get_midi_data(light_item)
    venue_data = get_midi_data(venue_item)
    #vg_log(venue_data)
    if verify_overwrite(light_data, "LIGHTING") != YES:
        return

    remove_events(light_data)
    remove_notes(light_data)

    pull_single_instance(venue_data, light_data, single_light_range)
    pull_faded_instance(venue_data, light_data, faded_lights_range)
    pull_faded_instance(venue_data, light_data, faded_procs_range)

    write_midi_data(light_item, light_data)
    #vg_log(light_data)
    
#pull_lighting_from_venue()
#pull_camera_from_venue()
