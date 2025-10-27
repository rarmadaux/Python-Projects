import customtkinter as ctk
import calendar as pycal
from datetime import datetime

def show(parent_frame):
    now = datetime.now()
    cal = pycal.month(now.year, now.month)

    label = ctk.CTkLabel(parent_frame, text=f"📅 Calendar {now.month}/{now.year}", font=("Arial", 20))
    label.pack(pady=10)

    text = ctk.CTkTextbox(parent_frame, width=300, height=200)
    text.insert("1.0", cal)
    text.configure(state="disabled")
    text.pack(pady=10)
