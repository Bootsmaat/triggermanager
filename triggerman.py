import tkinter as tk
from tkinter import ttk
from triggers import *

def add_list_item (trigger):
    lst_item    = tk.Frame (frame_trigger_list)
    lbl_id      = tk.Label (lst_item, text=str (trigger.id))
    lbl_name    = tk.Label (lst_item, text=str (trigger.name))

    lst_item.pack   (fill=tk.X, expand=1, anchor=tk.NW)
    lbl_id.pack     (side=tk.LEFT)
    lbl_name.pack   (side=tk.LEFT)

def add_item ():
    add_trigger ()
    add_list_item (trigger_list[-1])

root = tk.Tk ()
root.title ("triggerman")

# Setup scroll frame

container           = ttk.Frame (root)
canvas              = tk.Canvas (container)
scrollbar           = ttk.Scrollbar (container, orient="vertical", command=canvas.yview)
frame_trigger_list  = ttk.Frame (canvas)

frame_trigger_list.bind (
    "<Configure>",
    lambda e: canvas.configure (
        scrollregion = canvas.bbox ("all")
    )
)

canvas.create_window ((0,0), window=frame_trigger_list, anchor="nw")
canvas.configure (yscrollcommand=scrollbar.set)

btn_add         = tk.Button (root, text="add", command=add_item)
btn_remove      = tk.Button (root, text="remove", bg="red")
btn_copy        = tk.Button (root, text="copy")

# packing

container.pack  (fill=tk.BOTH, expand=1, anchor=tk.N)
canvas.pack     (side=tk.LEFT, fill=tk.BOTH, expand=1)
scrollbar.pack  (side=tk.RIGHT, fill=tk.Y)
btn_add.pack    (anchor=tk.NW, side=tk.LEFT, fill=tk.X)
btn_remove.pack (anchor=tk.NW, side=tk.LEFT, fill=tk.X)
btn_copy.pack   (anchor=tk.NW, side=tk.LEFT, fill=tk.X)

root.mainloop ()
