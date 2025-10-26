# created by rarmada
# 2025-09-27
# Project 7 - WAV to MP3 Converter with GUI
# python3.12 app.py

import customtkinter as ctk
import tkinter.filedialog as fd
from pydub import AudioSegment
import os
import sys
import json
import platform
import subprocess


# --- Helper for bundled resources (works in .exe and normal Python) ---
def resource_path(relpath: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller onefile."""
    if hasattr(sys, "_MEIPASS"):  # PyInstaller sets this when running bundled
        return os.path.join(sys._MEIPASS, relpath)
    return os.path.join(os.path.abspath("."), relpath)


# Point pydub to our bundled ffmpeg.exe (placed inside ffmpeg/ folder)
ffmpeg_bin = resource_path(os.path.join("ffmpeg", "ffmpeg.exe"))
if os.path.exists(ffmpeg_bin):
    AudioSegment.converter = ffmpeg_bin
    os.environ["PATH"] = os.pathsep.join([os.path.dirname(ffmpeg_bin), os.environ.get("PATH", "")])


class ConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("720x420")     # wider + taller
        self.minsize(640, 360)       # prevent tiny window
        self.resizable(True, True)   # allow user to resize

        self.title("WAV para MP3 Conversor")
        self.geometry("500x300")

       # Title label
        self.label = ctk.CTkLabel(self, text="WAV → MP3 Conversor", font=("Arial", 20))
        self.label.pack(pady=(20, 10))

        # --- Row with two buttons side by side ---
        btn_row = ctk.CTkFrame(self)
        btn_row.pack(pady=10)

        self.select_folder_btn = ctk.CTkButton(
            btn_row, text="Selecionar Pasta de exporte", command=self.select_output_folder, width=200
        )
        self.select_folder_btn.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="ew")

        self.select_button = ctk.CTkButton(
            btn_row, text="Selecionar WAV ", command=self.select_file, width=200
        )
        self.select_button.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="ew")

        # Make both columns expand evenly when window grows
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        # Status label
        self.status_label = ctk.CTkLabel(self, text="Nenhum ficheiro selecionado", wraplength=600)
        self.status_label.pack(pady=10)

        # Convert button
        self.convert_button = ctk.CTkButton(
            self, text="Converter", command=self.convert, state="disabled"
        )
        #add space between buttons
        self.convert_button.pack(pady=(10, 0))
        
        # Open Folder button (disabled until conversion is done)
        self.open_folder_button = ctk.CTkButton(
            self, text="abrir pasta de exporte", command=self.open_output_folder, state="disabled"
        )
        self.open_folder_button.pack(pady=10)
        self.convert_button.pack(pady=10)
        # Load last saved output folder (if exists)
        self.config_file = "config.json"
        self.output_folder = self.load_last_folder()
        if self.output_folder:
            self.status_label.configure(text=f"Pasta export (saved): {self.output_folder}")


    def open_output_folder(self):
        """Open the output folder in the file explorer."""
        if hasattr(self, "output_folder") and os.path.isdir(self.output_folder):
            if platform.system() == "Windows":
                os.startfile(self.output_folder)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.output_folder])
            else:  # Linux
                subprocess.Popen(["xdg-open", self.output_folder])

    def save_last_folder(self, folder):
        """Save the last output folder to config.json"""
        try:
            with open(self.config_file, "w") as f:
                json.dump({"output_folder": folder}, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def load_last_folder(self):
        """Load last output folder from config.json if available"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    return data.get("output_folder")
        except Exception as e:
            print(f"Error loading config: {e}")
        return None

    def select_file(self):
        file_path = fd.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.file_path = file_path
            self.status_label.configure(text=f"Selected: {file_path}")
            self.convert_button.configure(state="normal")

    def select_output_folder(self):
        folder = fd.askdirectory()
        if folder:
            self.output_folder = folder
            self.status_label.configure(text=f"Output folder: {folder}")
            self.save_last_folder(folder)

    def convert_then_split(self, input_wav: str, output_folder: str, max_size_mb: int = 10, safety_margin: float = 0.90):
        """Convert WAV → MP3, then split into multiple files if > max_size_mb * safety_margin."""
        base_filename = os.path.basename(input_wav).replace(".wav", "")
        wav = AudioSegment.from_wav(input_wav)

        # 1️⃣ Export full MP3
        full_mp3_path = os.path.join(output_folder, f"{base_filename}.mp3")
        wav.export(full_mp3_path, format="mp3", bitrate="128k")

        # 2️⃣ Check size
        max_bytes = int(max_size_mb * 1024 * 1024 * safety_margin)  # apply safety margin
        size_bytes = os.path.getsize(full_mp3_path)
        if size_bytes <= max_bytes:
            return [full_mp3_path]  # no need to split

        # 3️⃣ Split into parts
        segments = []
        bytes_per_ms = size_bytes / len(wav)
        start_ms = 0
        part = 1
        while start_ms < len(wav):
            slice_ms = int(max_bytes / bytes_per_ms)
            segment = wav[start_ms:start_ms + slice_ms]
            part_path = os.path.join(output_folder, f"{base_filename}_part{part}.mp3")
            segment.export(part_path, format="mp3", bitrate="128k")
            segments.append(part_path)
            start_ms += slice_ms
            part += 1

        # Remove original large MP3
        os.remove(full_mp3_path)
        return segments

    def convert(self):
        if not hasattr(self, "file_path"):
            self.status_label.configure(text="Nenhum Ficheiro selecionado!")
            return
        if not hasattr(self, "output_folder"):
            self.status_label.configure(text="Pasta exporte nao selecionada!")
            return

        try:
            output_files = self.convert_then_split(
                self.file_path, self.output_folder, max_size_mb=8
            )
            self.status_label.configure(
                text=f"Converted {len(output_files)} file(s) → {self.output_folder}"
            )
            self.open_folder_button.configure(state="normal")  # ✅ enable open folder
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # or "light"
    ctk.set_default_color_theme("blue")  # can be "dark-blue", "green", etc.
    ctk.set_widget_scaling(1.1)   # 1.0 = default; affects widget sizes

    app = ConverterApp()
    app.mainloop()
