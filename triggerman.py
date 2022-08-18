import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, font
from os import path 
from pathlib import Path
from triggers import *
import conman
# import exman as em
from config import *
from fizwatcher import fiz_watcher
from time import sleep
import fizprotocol as fp

root = tk.Tk()
root.title("triggermanager")
root.geometry("650x600")

cm = conman.conman()

cf = configurator()
config = cf.getConfig()

import fizlayoutpanel

# Load assets
img_icon_grey = tk.PhotoImage (file=path.join ('assets', 'status_icon_grey.gif'))
img_icon_red = tk.PhotoImage (file=path.join ('assets', 'status_icon_red.gif'))
img_icon_green = tk.PhotoImage (file=path.join ('assets', 'status_icon_green.gif'))

# gui globals
FLASH_LENGTH = 200

# globals
btn_submit = None
selected_item = tk.IntVar()
trigger_item_list = {}
trigger_loop_enabled = 0

string_f     = tk.StringVar ()
string_i     = tk.StringVar ()
string_z     = tk.StringVar ()
string_frame = tk.StringVar ()

string_f.set     ("00000")
string_i.set     ("00000")
string_z.set     ("00000")
string_frame.set ("00000")


# TODO check if refresh worked
def on_refresh_click():
    print("sending refresh opc")
    try:
        cm.send_opc(fp.OP_REFRESH)
    except ConnectionAbortedError as e:
        on_connection_error_event(e, btn_status_connection)


def on_connect_panel_close ():
    root.destroy ()

def on_root_close ():
    if messagebox.askokcancel ("Quit", "Are you sure?"):
        cm.cleanup()
        sleep(.1)
        root.destroy ()

def on_save ():
    print ('on_save: saving...')
    file = filedialog.asksaveasfilename (defaultextension='.json') # add some options here
    save (file, trigger_list)

def on_load ():
    global trigger_list
    print ('on_load: loading...')
    file = filedialog.askopenfilename (filetypes=[('JSON files', '.json')])
    trigger_data = [trigger_t(*a) for a in load(file)]
    trigger_list.clear ()
    clear_list ()

    for tr in trigger_data:
        trigger_list.append (tr)
        add_list_item (tr)

def on_open_playback ():
    v_files = [a.path for a in trigger_list if (Path (a.path).suffix == '.mp4') and a.enabled]
    # em.prep_video_player (v_files[0])

def on_stop_playback ():
    # em.stop_video ()
    print ("kill me")

def toggle_trigger_loop(widget = None):
    global trigger_loop_enabled, cb_i

    if trigger_loop_enabled:
        cm.send_opc(fp.OP_STOP)
        if (widget):
            widget['image'] = img_icon_grey
    else:
        if (widget):
            widget['image'] = img_icon_red
        cb_i = 0 # make sure we start with the first trigger

        cm.send_opc(fp.OP_START)
    
    trigger_loop_enabled = not trigger_loop_enabled

def connect_wrapper(window = None, error_field = None, connect_icon = None, entry_connection_string = None):
    global cm

    cm.cleanup()

    connection_string = entry_connection_string.get()

    # store address if it's modified
    if (connection_string != config['rpi_addr']):
        config['rpi_addr'] = connection_string

    try:
        cm = conman.conman()

        cm.connect(connection_string)
        cm.bind_error_callback(lambda a: on_connection_error_event (a, btn_status_connection))

        sleep(.1)
        fizWatcher = fiz_watcher(connection_string, string_f, string_i, string_z, string_frame)
        fizWatcher.start()

        cm.send_fiz_config(config['fiz_layout'])

    except BaseException as e:
        if (error_field):
            error_field.insert(tk.END, '\n')
            error_field.insert(tk.END, e)
        raise e
    else:
        connect_icon['image'] = img_icon_green
        if (window):
            window.destroy()

def send_config():

    btn_submit['bg'] = 'green'

    enabled_triggers    = [tr for tr in trigger_list if tr.enabled]
    a_files             = [a for a in enabled_triggers if (Path(a.path).suffix == '.wav')]
    v_files             = [a for a in enabled_triggers if (Path(a.path).suffix == '.mp4')]
    # ONLY BINDS .mp4 VID FILES TO PLAY!
    
    for a in a_files:
        # cm.bind_id (a.id, lambda t : em.play (get_trigger_by_id (t).path))
        print ("kill me")
    
    for v in v_files:
        print ("kill me")
        # cm.bind_id (v.id, lambda t : em.play_video (get_trigger_by_id (t).path))
    
    # let user do this with menu option
    # if (len (v_files) != 0):
    #     em.prep_video_player (v_files[0].path)

    print('sending list %s' % enabled_triggers)
    cm.send_trigger(enabled_triggers)

def open_file ():
    _path = filedialog.askopenfilename (
        filetypes=[
            # ("all files", "*.*"),
            ("Mp4 Files", "*.mp4"),
            ("WAV files", "*.wav")
        ]
    )
    return _path

def update_element(_item, **kwargs):
    for key in kwargs:
        _item[key] = kwargs[key]

def update_trigger_wrapper(widget, id, **kwargs):

    btn_submit['bg'] = 'red'

    orig_color = widget.cget ("background")

    if 'path' in kwargs:
        _path = open_file ()
        if not (len (_path) == 0):
            kwargs['path'] = _path # set kwargs to actual path
            widget['text'] = path.basename (_path)
            update_trigger (id=id, **kwargs)

    if 'activation_frame' in kwargs:
        try:
            kwargs['activation_frame'] = int (kwargs['activation_frame'])
        except ValueError:
            widget['bg'] = "red"
            widget.delete (0, tk.END)
        else:
            widget['bg'] = "green"
            update_trigger (id=id, **kwargs)

    if 'name' in kwargs:
        widget['bg'] = "green"
        update_trigger (id=id, **kwargs)

def add_list_item(trigger):
    global selected_item

    enabled = tk.IntVar()
    enabled.set(trigger.enabled)

    # root of item
    lst_item        = tk.Frame          (frame_trigger_list)

    btn_selected    = tk.Radiobutton    (lst_item, variable=selected_item, value=trigger.id)
    lbl_id          = tk.Label          (lst_item, text="%02i" % trigger.id)
    entry_name      = tk.Entry          (lst_item, fg='white', bg='red')
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
    entry_tframe    = tk.Entry (lst_item, fg='white', bg='red')

    entry_name.insert   (0, trigger.name)
    entry_name.bind     (
        "<Return>",
        lambda a: update_trigger_wrapper (
            widget=entry_name,
            id=trigger.id,
            name=entry_name.get ()
            )
        )
    entry_name.bind (
        "<FocusOut>",
        lambda a: on_entry_name_leave (widget=entry_name, id=trigger.id)
        )

    entry_tframe.insert (0, str (trigger.activation_frame))
    entry_tframe.bind   (
        "<Return>",
        lambda a: update_trigger_wrapper (
            widget=entry_tframe,
            id=trigger.id,
            activation_frame=entry_tframe.get ()
            )
    )
    entry_tframe.bind (
        "<FocusOut>",
        lambda a: on_entry_tframe_leave (widget=entry_tframe, id=trigger.id)
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

def on_entry_name_leave(widget=None, id=None):
    trigger = get_trigger_by_id(id)
    original_name = trigger.name

    if (original_name != widget.get()):
        widget['bg'] = 'red'

def on_entry_tframe_leave(widget=None, id=None):
    trigger = get_trigger_by_id (id)
    original_tframe = trigger.activation_frame

    if (original_tframe != int(widget.get ())):
        widget['bg'] = 'red'

def clear_list():
    for key in trigger_item_list:
        trigger_item_list[key].pack_forget()

def remove_item():
    selected_id = selected_item.get()
    remove_trigger(selected_id)
    trigger_item_list[selected_id].pack_forget()

# adds empty trigger and updated list window
def add_item():
    add_trigger()
    add_list_item(trigger_list[-1])

# raised when conman cant send data over socket
def on_connection_error_event (error, connection_widget):
    connection_widget['image'] = img_icon_grey

def spawnConnectionPanel():
    connect_panel = tk.Toplevel (root)
    connect_panel.title         ("connect")
    connect_panel.attributes    ("-topmost", True)
    connect_panel.grab_set      ()
    connect_panel.geometry      ("365x345")

    error_widget = scrolledtext.ScrolledText(connect_panel)
    error_widget.bind("<Key>", lambda e:"break")

    _entry_connection_string = tk.Entry(connect_panel)
    _entry_connection_string.insert(0, config['rpi_addr'])

    btn_connect = tk.Button(connect_panel, text="connect", 
        command=lambda: connect_wrapper(
            window=connect_panel,
            error_field=error_widget,
            connect_icon=btn_status_connection,
            entry_connection_string=_entry_connection_string
    ))

    _entry_connection_string.pack        (ipady=5, fill='x')
    btn_connect.pack                     (ipady=5, fill='x')
    error_widget.pack                    (expand=True, fill='both')

    connect_panel.protocol("WM_DELETE_WINDOW", on_connect_panel_close)

    return (connect_panel, error_widget, _entry_connection_string)

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
config_menu     = tk.Menu   (menubar, tearoff=0)

filemenu.add_command    (label="Save", command=on_save)
filemenu.add_command    (label="Load", command=on_load)
menubar.add_cascade     (label='File', menu=filemenu)

videomenu.add_command   (label='open playback window', command=on_open_playback)
videomenu.add_command   (label='stop video', command=on_stop_playback)
menubar.add_cascade     (label='Video', menu=videomenu)

config_menu.add_command (label='FIZ Layout', command=lambda: fizlayoutpanel.open_layout_panel(root, config, cm))
menubar.add_cascade     (label='Configuration', menu=config_menu)

font_highlight = font.Font (weight='bold', slant='italic')


# status bar 
status_bar              = tk.Frame  (root)
btn_status_connection   = tk.Button (status_bar, image=img_icon_grey)

btn_status_connection.configure(command=spawnConnectionPanel)

btn_status_shooting     = tk.Button(status_bar, image=img_icon_grey)

btn_refresh   = tk.Button(status_bar, text="reconnect USB")
btn_refresh.configure(command=on_refresh_click)

lbl_frame_status_hdr    = tk.Label(status_bar, text="Fr:", font=font_highlight)
lbl_frame_status        = tk.Label(status_bar, textvariable=string_frame)
lbl_focus_status_hdr    = tk.Label(status_bar, text="F:", font=font_highlight)
lbl_focus_status        = tk.Label(status_bar, textvariable=string_f)
lbl_iris_status_hdr     = tk.Label(status_bar, text="I:", font=font_highlight)
lbl_iris_status         = tk.Label(status_bar, textvariable=string_i)
lbl_zoom_status_hdr     = tk.Label(status_bar, text="Z:", font=font_highlight)
lbl_zoom_status         = tk.Label(status_bar, textvariable=string_z)

# control buttons
btn_add               = tk.Button(root, text="add", command=add_item)
btn_remove            = tk.Button(root, text="remove", bg="red", command=remove_item)
btn_submit            = tk.Button(
                                    root,
                                    text="send to pi",
                                    fg='white',
                                    bg='red',
                                    command=send_config
                                )
btn_shooting          = tk.Button(root, text="shoot", command=lambda: toggle_trigger_loop(btn_status_shooting))

# TODO replace with polling thread
btn_test = tk.Button(root, text="GET STATUS", command=lambda: cm.send_opc(fp.OP_STATUS))

# connect panel

spawnConnectionPanel()

# packing
status_bar.pack             (fill=tk.BOTH, anchor=tk.N, side=tk.TOP)
container.pack              (fill=tk.BOTH, expand=1, anchor=tk.N)
canvas.pack                 (side=tk.LEFT, fill=tk.BOTH, expand=1)
scrollbar.pack              (side=tk.RIGHT, fill=tk.Y)
btn_add.pack                (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_remove.pack             (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_submit.pack             (anchor=tk.NW, side=tk.RIGHT, fill=tk.X, pady=2, padx=2)
btn_shooting.pack           (anchor=tk.NW, side=tk.RIGHT, fill=tk.X, pady=2, padx=2)
btn_test.pack           (anchor=tk.NW, side=tk.RIGHT, fill=tk.X, pady=2, padx=2)

btn_status_connection.pack      (side=tk.LEFT, anchor=tk.NW)
btn_status_shooting.pack        (side=tk.LEFT, anchor=tk.NW)
btn_refresh.pack                (side=tk.LEFT, anchor=tk.NW)
lbl_frame_status_hdr.pack       (side=tk.LEFT, anchor=tk.NW)
lbl_frame_status.pack           (side=tk.LEFT, anchor=tk.NW)
lbl_focus_status_hdr.pack       (side=tk.LEFT, anchor=tk.NW)
lbl_focus_status.pack           (side=tk.LEFT, anchor=tk.NW)
lbl_iris_status_hdr.pack        (side=tk.LEFT, anchor=tk.NW)
lbl_iris_status.pack            (side=tk.LEFT, anchor=tk.NW)
lbl_zoom_status_hdr.pack        (side=tk.LEFT, anchor=tk.NW)
lbl_zoom_status.pack            (side=tk.LEFT, anchor=tk.NW)

root.config(menu=menubar)
root.protocol("WM_DELETE_WINDOW", on_root_close)
root.mainloop()
