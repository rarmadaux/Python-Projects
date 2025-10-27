import customtkinter as ctk
import game, calendar   # import modules

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Modular App Example")
app.geometry("800x500")

# --- Navbar ---
navbar = ctk.CTkFrame(app, height=50, corner_radius=0)
navbar.pack(side="top", fill="x")

# --- Sidebar ---
sidebar = ctk.CTkFrame(app, width=150, corner_radius=0)
sidebar.pack(side="left", fill="y")

# --- Main content (swappable) ---
content = ctk.CTkFrame(app)
content.pack(side="left", fill="both", expand=True, padx=10, pady=10)

def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

def load_game():
    clear_content()
    game.show(content)

def load_calendar():
    clear_content()
    calendar.show(content)

def load_converter():
    clear_content()
    converter.show(content)

# Sidebar buttons
btn1 = ctk.CTkButton(sidebar, text="Game", command=load_game)
btn1.pack(pady=10, padx=10)

btn2 = ctk.CTkButton(sidebar, text="Calendar", command=load_calendar)
btn2.pack(pady=10, padx=10)

btn3 = ctk.CTkButton(sidebar, text="Converter", command=load_converter)
btn3.pack(pady=10, padx=10)

app.mainloop()
