# created by rarmada
# 2025-09-27
# Project 7 - WAV to MP3 Converter with GUI
# python3.12 app.py

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
        self.select_folder_btn = ctk.CTkButton(
            self, text="Select Output Folder", command=self.select_output_folder
        )
        self.select_folder_btn.pack(pady=10)

        # Select file button
        self.select_button = ctk.CTkButton(
            self, text="Select WAV File", command=self.select_file
        )
        self.select_button.pack(pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(self, text="No file selected", wraplength=400)
        self.status_label.pack(pady=10)

        # Convert button
        self.convert_button = ctk.CTkButton(
            self, text="Convert", command=self.convert, state="disabled"
        )
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
            self.status_label.configure(text="No file selected!")
            return
        if not hasattr(self, "output_folder"):
            self.status_label.configure(text="No output folder selected!")
            return

        try:
            output_files = self.convert_then_split(
                self.file_path, self.output_folder, max_size_mb=10
            )
            self.status_label.configure(
                text=f"Converted {len(output_files)} file(s) → {self.output_folder}"
            )
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # or "light"
    ctk.set_default_color_theme("blue")  # can be "dark-blue", "green", etc.

    app = ConverterApp()
    app.mainloop()
