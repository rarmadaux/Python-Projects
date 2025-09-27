# created by rarmada
# 2025-09-27
# Project 7 - WAV to MP3 Converter with GUI

import customtkinter as ctk
import tkinter.filedialog as fd
from pydub import AudioSegment
import os


class ConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WAV to MP3 Converter")
        self.geometry("500x300")

        # Title label
        self.label = ctk.CTkLabel(self, text="WAV → MP3 Converter", font=("Arial", 20))
        self.label.pack(pady=20)

        # Select output folder
        self.select_folder_btn = ctk.CTkButton(self, text="Select Output Folder", command=self.select_output_folder)
        self.select_folder_btn.pack(pady=10)

        # Select file button
        self.select_button = ctk.CTkButton(self, text="Select WAV File", command=self.select_file)
        self.select_button.pack(pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(self, text="No file selected", wraplength=400)
        self.status_label.pack(pady=10)

        # Convert button
        self.convert_button = ctk.CTkButton(self, text="Convert", command=self.convert, state="disabled")
        self.convert_button.pack(pady=10)

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
            self.update_status()

    def convert(self):
        if not hasattr(self, "file_path"):
            self.status_label.configure(text="No file selected!")
            return
        if not hasattr(self, "output_folder"):
            self.status_label.configure(text="No output folder selected!")
            return

        try:
            wav = AudioSegment.from_wav(self.file_path)

            # Save MP3 in the user-selected folder
            filename = os.path.basename(self.file_path).replace(".wav", ".mp3")
            out_path = os.path.join(self.output_folder, filename)

            wav.export(out_path, format="mp3", bitrate="128k")  # compress with 128 kbps

            self.status_label.configure(text=f"Converted → {out_path}")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")



if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # or "light"
    ctk.set_default_color_theme("blue")  # can be "dark-blue", "green", etc.

    app = ConverterApp()
    app.mainloop()
