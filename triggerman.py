import tkinter as tk
from tkinter import filedialog, IntVar
from os import path
from triggers import *
import conman as cm
import exman as em

root = tk.Tk ()
root.title ("triggerman")
root.geometry ("650x600")

# gui globals
FLASH_LENGTH = 200

# globals

selected_item = IntVar()
trigger_item_list = []
trigger_loop_enabled = 0

def toggle_trigger_loop ():
    global trigger_loop_enabled, cb_i

    if trigger_loop_enabled:
        print ('stopping thread')
        cm.send_opc (cm.OP_STOP)
    else:
        print ('starting thread')

        cb_i = 0 # make sure we start with the first trigger

        # maybe put this in cm.send_trigger?
        # sort list based on activation frame
        cm.callbacks.sort (key=lambda t: t[1])

        # get all paths from triggers
        files = [p.path for p in trigger_list]
        em.prep_players (files)

        cm.send_opc (cm.OP_START)
    
    trigger_loop_enabled = not trigger_loop_enabled

def connect_wrapper ():
    cm.connect ('PiTwo.local')
    cm.send_opc (cm.OP_FD)

def send_config ():
    enabled_triggers = []
    for tr in trigger_list:
        if tr.enabled:
            enabled_triggers.append (tr)
            cm.bind_id (tr.id, tr.activation_frame, lambda:em.skip ())
    
    print ('sending list %s' % enabled_triggers)
    cm.send_trigger (enabled_triggers)

def open_file ():
    _path = filedialog.askopenfilename (
        filetypes=[
            ("all files", "*.*"),
            ("Mp3 Files", "*.mp3"),
            ("WAV files", "*.wav")
        ]
    )
    return _path

def update_element (_item, **kwargs):
    for key in kwargs:
        _item[key] = kwargs[key]

def update_trigger_wrapper (_item, _id, **kwargs):

    orig_color = _item.cget ("background")

    if 'path' in kwargs:
        _path = open_file ()
        if not (len (_path) == 0):
            kwargs['path'] = _path # set kwargs to actual path
            _item['text'] = path.basename (_path)

    if 'activation_frame' in kwargs:
        try:
            kwargs['activation_frame'] = int (kwargs['activation_frame'])
        except ValueError:
            _item['bg'] = "red"
            _item.delete (0, tk.END)
        else:
            _item['bg'] = "green"
            update_trigger (id=_id, **kwargs)
        finally:
            _item.after (FLASH_LENGTH, lambda: update_element (_item, bg=orig_color))
    else:
        _item['bg'] = "green"
        update_trigger (id=_id, **kwargs)
        _item.after (FLASH_LENGTH, lambda: update_element (_item, bg=orig_color))


def add_list_item (trigger):
    global selected_item

    enabled = IntVar ()
    enabled.set (trigger.enabled)

    # root of item
    lst_item        = tk.Frame          (frame_trigger_list)

    btn_selected    = tk.Radiobutton    (lst_item, variable=selected_item, value=trigger.id)
    lbl_id          = tk.Label          (lst_item, text="%02i" % trigger.id)
    entry_name      = tk.Entry          (lst_item)
    btn_filepath    = tk.Button         (
        lst_item,
        text=trigger.path,
        command=lambda: update_trigger_wrapper (
            btn_filepath,
            trigger.id,
            path=1
        )
    )
    lbl_enabled     = tk.Label          (lst_item, text="enabled:")
    btn_enabled     = tk.Checkbutton    (
        lst_item,
        variable=enabled,
        command=lambda: update_trigger_wrapper (
            btn_enabled,
            trigger.id,
            enabled=enabled.get ()
        )
    )
    entry_tframe    = tk.Entry          (lst_item)

    entry_name.insert   (0, trigger.name)
    entry_name.bind     (
        "<Return>",
        lambda a: update_trigger_wrapper (
            _item=entry_name,
            _id=trigger.id,
            name=entry_name.get ()
            )
        )

    entry_tframe.insert (0, str (trigger.activation_frame))
    entry_tframe.bind   (
        "<Return>",
        lambda a: update_trigger_wrapper (
            _item=entry_tframe,
            _id=trigger.id,
            activation_frame=entry_tframe.get ()
            )
    )

    lst_item.pack       (fill=tk.X, expand=1, anchor=tk.NW)
    btn_selected.pack   (side=tk.LEFT, padx=1, pady=1)
    lbl_id.pack         (side=tk.LEFT, padx=1, pady=1)
    lbl_enabled.pack    (side=tk.LEFT, padx=2, pady=1)
    btn_enabled.pack    (side=tk.LEFT)
    entry_name.pack     (side=tk.LEFT, padx=2, pady=1)
    btn_filepath.pack   (side=tk.LEFT, padx=2, pady=1)
    entry_tframe.pack   (side=tk.LEFT, padx=2, pady=1)

    trigger_item_list.append (lst_item)

def remove_item ():
    remove_trigger (selected_item.get ())
    trigger_item_list[selected_item.get ()].pack_forget ()

def add_item ():
    add_trigger ()
    add_list_item (trigger_list[-1])

# Setup scroll frame

container           = tk.Frame (root)
canvas              = tk.Canvas (container)
scrollbar           = tk.Scrollbar (container, orient="vertical", command=canvas.yview)
frame_trigger_list  = tk.Frame (canvas)

frame_trigger_list.bind (
    "<Configure>",
    lambda e: canvas.configure (
        scrollregion = canvas.bbox ("all")
    )
)

canvas.create_window ((0,0), window=frame_trigger_list, anchor="nw")
canvas.configure (yscrollcommand=scrollbar.set)

btn_add         = tk.Button (root, text="add", command=add_item)
btn_remove      = tk.Button (root, text="remove", bg="red", command=remove_item)
btn_copy        = tk.Button (root, text="copy")
btn_send_cnf    = tk.Button (root, text="send to pi", command=send_config)
btn_shooting    = tk.Button (root, text="shoot", command=toggle_trigger_loop)
btn_connect     = tk.Button (root, text="connect", command=connect_wrapper)

# packing
container.pack      (fill=tk.BOTH, expand=1, anchor=tk.N)
canvas.pack         (side=tk.LEFT, fill=tk.BOTH, expand=1)
scrollbar.pack      (side=tk.RIGHT, fill=tk.Y)
btn_add.pack        (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_remove.pack     (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_copy.pack       (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_send_cnf.pack   (anchor=tk.NW, side=tk.RIGHT, fill=tk.X, pady=2, padx=2)
btn_shooting.pack   (anchor=tk.NW, side=tk.RIGHT, fill=tk.X, pady=2, padx=2)
btn_connect.pack    (anchor=tk.NW, side=tk.RIGHT, fill=tk.X, pady=2, padx=2)

cm.thr.register_tr_cb (cm.on_fire_trigger)

root.mainloop ()
