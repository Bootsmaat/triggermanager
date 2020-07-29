import tkinter as tk
from tkinter import ttk

root = tk.Tk ()
root.title ("triggerman")

container = ttk.Frame (root)
canvas = tk.Canvas (container)
scrollbar = ttk.Scrollbar (container, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame (canvas)

scrollable_frame.bind (
    "<Configure>",
    lambda e: canvas.configure (
        scrollregion = canvas.bbox ("all")
    )
)

canvas.create_window ((0,0), window=scrollable_frame, anchor="nw")
canvas.configure (yscrollcommand=scrollbar.set)


container.pack (fill=tk.X, expand=1, anchor=tk.N)
canvas.pack (side=tk.LEFT, fill=tk.BOTH, expand=1)
scrollbar.pack (side=tk.RIGHT, fill=tk.Y)

for i in range (0,50):
    ttk.Label (scrollable_frame, text=str (i)).pack ()

root.mainloop ()
