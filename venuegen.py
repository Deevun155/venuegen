import os
import sys
from tkinter import Tk, Button, Label, Checkbutton, IntVar, Toplevel, Frame
from tkinter.ttk import Separator
from vgprocess import generate_venue, copy_camera_to_venue, copy_lights_to_venue
from vgreverse import pull_camera_from_venue, pull_lighting_from_venue

path = os.path.join(sys.path[0], "venuegen.ini")
with open(path, 'r') as f:
    config = {}
    for line in f:
        k, v = line.strip().split('=')
        config[k.strip()] = v.strip()
autoclose_enabled = (config['autoclose'] == '1') if 'autoclose' in config else False
skip_overwrite_prompt = (config.get('skip_overwrite_prompt', '0') == '1')

def write_config():
    with open(path, 'w') as f:
        for k, v in config.items():
            f.write(f"{k}={v}\n")

def generate_and_overwrite():
    def on_confirm():
        if dont_show_again.get():
            config['skip_overwrite_prompt'] = '1'
            write_config()
        prompt.destroy()
        generate_venue()
        copy_lights_to_venue(force=True)
        copy_camera_to_venue(force=True)
        if autoclose_enabled:
            form.destroy()

    if not skip_overwrite_prompt:
        prompt = Toplevel(form)
        prompt.title("Confirm Overwrite")
        Label(prompt, text="This option will overwrite any text events currently in the VENUE track. Are you sure you want to continue?").pack(padx=10, pady=10)
        dont_show_again = IntVar()
        Checkbutton(prompt, text="Don't show again", variable=dont_show_again).pack(pady=5)
        
        button_frame = Frame(prompt)
        button_frame.pack(pady=10)

        Button(button_frame, text="Yes", command=on_confirm).pack(side="left", padx=5)
        Button(button_frame, text="No", command=prompt.destroy).pack(side="right", padx=5)
    else:
        generate_venue()
        copy_lights_to_venue(force=True)
        copy_camera_to_venue(force=True)
        if autoclose_enabled:
            form.destroy()

def main():
    def autoclose():
        if autoclose_enabled:
            form.destroy()

    global form
    form = Tk()
    form.title("venuegen")
    form.minsize(height=160, width=74)

    Label(form, text="Apply to VENUE").grid(row=0, column=0, pady=5)
    Label(form, text="Apply to CAMERA/LIGHTING").grid(row=0, column=2, pady=5)

    Separator(form, orient="vertical").grid(row=0, column=1, rowspan=4, sticky="ns", padx=5)

    btn_cpylight = Button(form, text="Copy LIGHTING to VENUE",
            width=22, command=lambda: [copy_lights_to_venue(), autoclose()])
    btn_cpylight.grid(row=1, column=0, padx=3, pady=3, sticky="w")

    btn_cpycam = Button(form, text="Copy CAMERA to VENUE",
            width=22, command=lambda: [copy_camera_to_venue(), autoclose()])
    btn_cpycam.grid(row=2, column=0, padx=3, pady=3, sticky="w")

    btn_pulllight = Button(form, text="Pull LIGHTING from VENUE",
            width=22, command=lambda: [pull_lighting_from_venue(), autoclose()])
    btn_pulllight.grid(row=1, column=2, padx=3, pady=3, sticky="e")

    btn_pullcam = Button(form, text="Pull CAMERA from VENUE",
            width=22, command=lambda: [pull_camera_from_venue(), autoclose()])
    btn_pullcam.grid(row=2, column=2, padx=3, pady=3, sticky="e") 

    btn_generate = Button(form, text="Generate!",
            width=30, command=lambda: [generate_venue(), autoclose()])
    btn_generate.grid(row=4, column=0, columnspan=3, padx=3, pady=3)

    btn_generate_overwrite = Button(form, text="Generate and Overwrite!",
            width=30, command=generate_and_overwrite)
    btn_generate_overwrite.grid(row=5, column=0, columnspan=3, padx=3, pady=3)

    form.mainloop()

if __name__ == "__main__":
    main()
