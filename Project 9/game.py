import customtkinter as ctk

def show(parent_frame):
    label = ctk.CTkLabel(parent_frame, text="🎮 Simple Game", font=("Arial", 20))
    label.pack(pady=20)

    btn = ctk.CTkButton(parent_frame, text="Click Me!", command=lambda: label.configure(text="You clicked!"))
    btn.pack(pady=10)
