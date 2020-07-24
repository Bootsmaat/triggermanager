import tkinter as tk

windows = tk.Tk ()

msg = tk.Label (
    text = "sup dog",
    width = 40,
    height = 20
)

btn = tk.Button (
    text = "test",
    width = 25
)

msg.pack ()
btn.pack ()

windows.mainloop ()
