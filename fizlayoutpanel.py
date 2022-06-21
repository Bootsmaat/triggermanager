import tkinter as tk
from tkinter import ttk
from conman import send_fiz_config

is_panel_open = False

layout_positions = [
    "Disabled",
    "0",
    "1",
    "2",
    "3"
]

pos_focus   = tk.StringVar ()
pos_iris    = tk.StringVar ()
pos_zoom    = tk.StringVar ()
pos_frameNr = tk.StringVar ()

# fuck this dumb function, shouldnt be necessary if server can accept a more sane command instead of a string
def get_fiz_string ():
    pos_list = []

    try:
        pos_list.append (('F', int(pos_focus.get())))
    except:
        pass
    try:
        pos_list.append (('I', int(pos_iris.get())))
    except:
        pass
    try:
        pos_list.append (('Z', int(pos_zoom.get())))
    except:
        pass
    try:
        pos_list.append (('f', int(pos_frameNr.get())))
    except:
        pass

    pos_list.sort (key=lambda tup: tup[1])

    return_string = ""
    for tup in pos_list:
        return_string = return_string + tup[0]
    
    return return_string

def on_submit ():
    send_fiz_config( get_fiz_string () )

def open_layout_panel (root):
    print ('opens the fiz layout panel')

    window = tk.Toplevel (root)
    window.title ("FIZ Layout")
    window.geometry ("365x120")

    frame_focus         = tk.Frame (window)
    frame_iris          = tk.Frame (window)
    frame_zoom          = tk.Frame (window)
    frame_frameNr       = tk.Frame (window)

    lbl_focus       = tk.Label (frame_focus, text="Focus:")
    lbl_iris        = tk.Label (frame_iris, text="Iris:")
    lbl_zoom        = tk.Label (frame_zoom, text="Zoom:")
    lbl_framenumber = tk.Label (frame_frameNr, text="Frame Nr.:")

    combox_focus    = ttk.Combobox (frame_focus, values=layout_positions, textvariable=pos_focus)
    combox_iris     = ttk.Combobox (frame_iris, values=layout_positions, textvariable=pos_iris)
    combox_zoom     = ttk.Combobox (frame_zoom, values=layout_positions, textvariable=pos_zoom)
    combox_frameNr  = ttk.Combobox (frame_frameNr, values=layout_positions, textvariable=pos_frameNr)

    combox_focus    .current (1)
    combox_iris     .current (0)
    combox_zoom     .current (0)
    combox_frameNr  .current (2)

    frame_focus     .pack (anchor=tk.NW, fill=tk.X)
    frame_iris      .pack (anchor=tk.NW, fill=tk.X)
    frame_zoom      .pack (anchor=tk.NW, fill=tk.X)
    frame_frameNr   .pack (anchor=tk.NW, fill=tk.X)

    btn_submit = tk.Button (window, text="Submit", command=on_submit, padx=2)

    lbl_focus.pack (anchor=tk.NW, side=tk.LEFT)
    combox_focus.pack (anchor=tk.NE, side=tk.RIGHT)

    lbl_iris.pack (anchor=tk.NW, side=tk.LEFT)
    combox_iris.pack (anchor=tk.NE, side=tk.RIGHT)

    lbl_zoom.pack (anchor=tk.NW, side=tk.LEFT)
    combox_zoom.pack (anchor=tk.NE, side=tk.RIGHT)

    lbl_framenumber.pack (anchor=tk.NW, side=tk.LEFT)
    combox_frameNr.pack (anchor=tk.NE, side=tk.RIGHT)

    btn_submit.pack (anchor=tk.S, side=tk.BOTTOM)

