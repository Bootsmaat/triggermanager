import tkinter as tk

root = tk.Tk ()

lst_triggers = tk.Listbox (root, selectmode=tk.SINGLE)

for i in range (0, 20):
    lst_triggers.insert (tk.END, str (i))

lst_triggers.pack (fill=tk.Y, expand=1)