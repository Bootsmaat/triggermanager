import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, font
from os import path 
from pathlib import Path
from triggers import *
import conman as cm
import exman as em
from saver import save, load

root = tk.Tk ()
root.title ("triggerman (V1.0)")
root.geometry ("650x600")

# Load assets
img_icon_grey = tk.PhotoImage (file=path.join ('assets', 'status_icon_grey.gif'))
img_icon_red = tk.PhotoImage (file=path.join ('assets', 'status_icon_red.gif'))
img_icon_green = tk.PhotoImage (file=path.join ('assets', 'status_icon_green.gif'))

# gui globals
FLASH_LENGTH = 200

# globals
selected_item = tk.IntVar()
trigger_item_list = {}
trigger_loop_enabled = 0

# TODO Custom option should expand to fill in ip address
conn_options = [
    "IronPi.local",
    "PiTwo.local",
    # "Custom..."
]
# storing the option for which address to connect to
conn_addr_str = tk.StringVar()
conn_addr_str.set (conn_options[0])

def on_connect_panel_close ():
    root.destroy ()

def on_root_close ():
    if messagebox.askokcancel ("Quit", "Are you sure?"):
        cm.sock.close ()
        cm.thr.stop ()
        root.destroy ()

def on_save ():
    print ('on_save: saving...')
    file = filedialog.asksaveasfilename (defaultextension='.jad') # add some options here
    save (file, trigger_list)

def on_load ():
    global trigger_list
    print ('on_load: loading...')
    file = filedialog.askopenfilename (filetypes=[('jad files', '.jad')])
    trigger_data = [trigger_t (*a) for a in load (file)]
    trigger_list.clear ()
    clear_list ()

    for tr in trigger_data:
        trigger_list.append (tr)
        add_list_item (tr)

def on_open_playback ():
    v_files = [a.path for a in trigger_list if (Path (a.path).suffix == '.mp4') and a.enabled]
    em.prep_video_player (v_files[0])

def on_stop_playback ():
    em.stop_video ()

def toggle_trigger_loop ():
    global trigger_loop_enabled, cb_i

    if trigger_loop_enabled:
        cm.send_opc (cm.OP_STOP)
    else:
        cb_i = 0 # make sure we start with the first trigger

        cm.send_opc (cm.OP_START)
    
    trigger_loop_enabled = not trigger_loop_enabled

def connect_wrapper (window = None, error_field = None, connect_icon = None):
    try:
        cm.connect (conn_addr_str.get ())
        cm.send_opc (cm.OP_FD)
    except BaseException as e:
        error_field.insert (tk.END, e)
    else:
        connect_icon['image'] = img_icon_green
        if (window):
            window.destroy ()


def send_config ():
    enabled_triggers    = [tr for tr in trigger_list if tr.enabled]
    a_files             = [a for a in enabled_triggers if (Path (a.path).suffix == '.wav')]
    v_files             = [a for a in enabled_triggers if (Path (a.path).suffix == '.mp4')]
    # ONLY BINDS .mp4 VID FILES TO PLAY!
    
    for a in a_files:
        cm.bind_id (a.id, lambda t : em.play (get_trigger_by_id (t).path))
    
    for v in v_files:
        cm.bind_id (v.id, lambda t : em.play_video (get_trigger_by_id (t).path))
    
    # let user do this with menu option
    # if (len (v_files) != 0):
    #     em.prep_video_player (v_files[0].path)

    print ('sending list %s' % enabled_triggers)
    cm.send_trigger (enabled_triggers)

def open_file ():
    _path = filedialog.askopenfilename (
        filetypes=[
            # ("all files", "*.*"),
            ("Mp4 Files", "*.mp4"),
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

    enabled = tk.IntVar ()
    enabled.set (trigger.enabled)

    # root of item
    lst_item        = tk.Frame          (frame_trigger_list)

    btn_selected    = tk.Radiobutton    (lst_item, variable=selected_item, value=trigger.id)
    lbl_id          = tk.Label          (lst_item, text="%02i" % trigger.id)
    entry_name      = tk.Entry          (lst_item)
    btn_filepath    = tk.Button         (
        lst_item,
        text=path.basename(trigger.path),
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

    trigger_item_list[trigger.id] = lst_item

def clear_list ():
    for key in trigger_item_list:
        trigger_item_list[key].pack_forget ()

def remove_item ():
    selected_id = selected_item.get ()
    remove_trigger (selected_id)
    trigger_item_list[selected_id].pack_forget ()

def add_item ():
    add_trigger ()
    add_list_item (trigger_list[-1])


# Setup scroll frame

container           = tk.Frame      (root)
canvas              = tk.Canvas     (container)
scrollbar           = tk.Scrollbar  (container, orient="vertical", command=canvas.yview)
frame_trigger_list  = tk.Frame      (canvas)

frame_trigger_list.bind (
    "<Configure>",
    lambda e: canvas.configure (
        scrollregion = canvas.bbox ("all")
    )
)

canvas.create_window ((0,0), window=frame_trigger_list, anchor="nw")
canvas.configure (yscrollcommand=scrollbar.set)

menubar         = tk.Menu   (root)

filemenu        = tk.Menu   (menubar, tearoff=0)
videomenu       = tk.Menu   (menubar, tearoff=0)

filemenu.add_command    (label="Save", command=on_save)
filemenu.add_command    (label="Load", command=on_load)
menubar.add_cascade     (label='File', menu=filemenu)

videomenu.add_command   (label='open playback window', command=on_open_playback)
videomenu.add_command   (label='stop video', command=on_stop_playback)
menubar.add_cascade     (label='Video', menu=videomenu)

font_highlight = font.Font (weight='bold', slant='italic')

# status bar 
status_bar              = tk.Frame  (root)
btn_status_connection   = tk.Button (status_bar, image=img_icon_grey)
btn_status_shooting     = tk.Button (status_bar, image=img_icon_grey)
lbl_frame_status_hdr    = tk.Label  (status_bar, text="Fr:", font=font_highlight)
lbl_frame_status        = tk.Label  (status_bar, text="00000")
lbl_focus_status_hdr    = tk.Label  (status_bar, text="F:", font=font_highlight)
lbl_focus_status        = tk.Label  (status_bar, text="00000")
lbl_iris_status_hdr     = tk.Label  (status_bar, text="I:", font=font_highlight)
lbl_iris_status         = tk.Label  (status_bar, text="00000")
lbl_zoom_status_hdr     = tk.Label  (status_bar, text="Z:", font=font_highlight)
lbl_zoom_status         = tk.Label  (status_bar, text="00000")


# control buttons
btn_add               = tk.Button (root, text="add", command=add_item)
btn_remove            = tk.Button (root, text="remove", bg="red", command=remove_item)
btn_copy              = tk.Button (root, text="copy")
btn_send_cnf          = tk.Button (root, text="send to pi", command=send_config)
btn_shooting          = tk.Button (root, text="shoot", command=toggle_trigger_loop)

# connect panel
connect_panel = tk.Toplevel (root)
connect_panel.title         ("connect")
connect_panel.attributes    ("-topmost", True)
connect_panel.grab_set      ()
connect_panel.geometry      ("365x345")

address_picker_menu = tk.OptionMenu (connect_panel, conn_addr_str, *conn_options)

error_widget = scrolledtext.ScrolledText (connect_panel)
error_widget.bind                        ("<Key>", lambda e:"break")



# packing
status_bar.pack             (fill=tk.BOTH, anchor=tk.N, side=tk.TOP)
container.pack              (fill=tk.BOTH, expand=1, anchor=tk.N)
canvas.pack                 (side=tk.LEFT, fill=tk.BOTH, expand=1)
scrollbar.pack              (side=tk.RIGHT, fill=tk.Y)
btn_add.pack                (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_remove.pack             (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_copy.pack               (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_send_cnf.pack           (anchor=tk.NW, side=tk.RIGHT, fill=tk.X, pady=2, padx=2)
btn_shooting.pack           (anchor=tk.NW, side=tk.RIGHT, fill=tk.X, pady=2, padx=2)

btn_status_connection.pack      (side=tk.LEFT, anchor=tk.NW)
btn_status_shooting.pack        (side=tk.LEFT, anchor=tk.NW)
lbl_frame_status_hdr.pack       (side=tk.LEFT, anchor=tk.NW)
lbl_frame_status.pack           (side=tk.LEFT, anchor=tk.NW)
lbl_focus_status_hdr.pack       (side=tk.LEFT, anchor=tk.NW)
lbl_focus_status.pack           (side=tk.LEFT, anchor=tk.NW)
lbl_iris_status_hdr.pack        (side=tk.LEFT, anchor=tk.NW)
lbl_iris_status.pack            (side=tk.LEFT, anchor=tk.NW)
lbl_zoom_status_hdr.pack        (side=tk.LEFT, anchor=tk.NW)
lbl_zoom_status.pack            (side=tk.LEFT, anchor=tk.NW)

btn_connect = tk.Button     (connect_panel, text="connect", 
command=lambda: connect_wrapper (window=connect_panel, error_field=error_widget, connect_icon=btn_status_connection))

btn_connect.pack            (anchor=tk.NW)
address_picker_menu.pack    (anchor=tk.NW)
error_widget.pack           (anchor=tk.N, padx=5, pady=5)

cm.thr.register_tr_cb (cm.on_fire_trigger)

root.config (menu=menubar)
connect_panel.protocol ("WM_DELETE_WINDOW", on_connect_panel_close)
root.protocol ("WM_DELETE_WINDOW", on_root_close)
root.mainloop ()
