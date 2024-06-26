#  Image Attribution for eye icons: icons created by th studio

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("800x480")
root.resizable(False, False)  # Corrected attribute name
root.title("Railway Products Group Tool Locker")

login_frame = tk.Frame(root)
login_frame.pack(pady=10)
login_frame.pack_propagate(False)
login_frame.configure(height=480, width=750, bg="light gray")

title_lbl = tk.Label(login_frame, text="Railway Products Group Tool Locker System", font=("Bold", 24, "underline"),
                     background="light gray", foreground="red")
title_lbl.pack()

user_id_lbl = tk.Label(login_frame, text="Please Enter User ID:", font=("Bold", 12, "underline"),
                       background="light gray")
user_id_lbl.pack(pady=25)

user_id_entry = tk.Entry(login_frame, font=("Bold", 15), width=25, show="*")
user_id_entry.focus()
user_id_entry.pack()

root.mainloop()
