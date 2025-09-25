# created by rarmada
# 2025-09-24
# Project 5 - Jarvis Voice Assistant with Ollama

"""

DESCRIPTION:
This project allows voice interaction with Ollama LLM, optional file searching, and speech output.
- Speak to Jarvis using your microphone.
- Jarvis can read local text files in ./files if you explicitly ask.
- Responses are spoken with a human-like voice using gTTS.
- Ollama is run inside a Docker container.

REQUIREMENTS:

1. Python 3.13+ or compatible
   - Ensure Python and pip are installed.

2. Docker
   - Install Docker for your OS: https://docs.docker.com/get-docker/
   - Ensure Ollama Docker container is available and named "ollama".
   - Commands:
       docker pull ollama/ollama
       docker run -d --name ollama -p 11434:11434 ollama/ollama

3. Python packages
   Install these packages using pip:

   pip install requests
   pip install gtts
   pip install pygame
   pip install whisper
   pip install sounddevice
   pip install numpy

   Notes:
   - gTTS: Google Text-to-Speech for natural voice output.
   - pygame: Plays audio output reliably on Linux.
   - whisper: Speech-to-Text offline model.
   - sounddevice: Captures microphone audio.
   - numpy: Required for audio processing.

4. Linux users
   - Ensure microphone works and is accessible.
   - Test with:
       arecord -l
       arecord -d 5 test.wav
       aplay test.wav

5. Files
   - Create a folder named 'files' in the same directory.
   - Add any .txt files you want Jarvis to optionally search.

HOW TO USE:
1. Make sure Docker container "ollama" is running (Jarvis can start it automatically).
2. Run the script:
       python3 jarvis.py
3. Speak to Jarvis when prompted.
4. Say "exit" to quit.

"""

import subprocess
import requests
import time
import os

from gtts import gTTS
import pygame
import whisper
import sounddevice as sd
import numpy as np

# ---------------------- Configuration ----------------------
DOCKER_CONTAINER = "ollama"
MODEL = "mistral"
FILES_DIR = "./files"  # adjust if needed

# ---------------------- Text-to-Speech ----------------------
def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("reply.mp3")
    
    pygame.mixer.init()
    pygame.mixer.music.load("reply.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

# ---------------------- Speech-to-Text ----------------------
whisper_model = whisper.load_model("small")

def listen_from_mic(duration=5, fs=16000):
    print(f"Listening for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    audio = np.squeeze(recording)
    result = whisper_model.transcribe(audio, fp16=False)
    return result["text"]

# ---------------------- Load files ----------------------
def load_files():
    documents = {}
    for filename in os.listdir(FILES_DIR):
        path = os.path.join(FILES_DIR, filename)
        if os.path.isfile(path) and filename.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                documents[filename] = f.read()
    return documents

# ---------------------- Docker management ----------------------
def start_Jarvis():
    print("Starting Jarvis container...")
    subprocess.run(["docker", "start", DOCKER_CONTAINER])
    time.sleep(5)
    print("Jarvis started!")

def stop_Jarvis():
    print("Stopping Jarvis container...")
    subprocess.run(["docker", "stop", DOCKER_CONTAINER])
    print("Jarvis stopped!")

# ---------------------- Chat with Jarvis ----------------------
def chat(documents):
    print("Chat with Jarvis! Say 'exit' to quit.")
    while True:
        # Capture user voice
        prompt = listen_from_mic(duration=7)  # 7 seconds to speak
        print("You said:", prompt)
        if prompt.lower() in ["exit", "quit","Exit.","Quit."]:
            break
        
        # Only search files if user asks explicitly
        if any(k in prompt.lower() for k in ["search", "lookup", "check file"]):
            context = "\n\n".join([f"{name}:\n{content}" for name, content in documents.items()])
            full_prompt = f"Answer the question based on the following files:\n{context}\n\nQuestion: {prompt}"
        else:
            full_prompt = prompt
        
        # Send prompt to Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": MODEL, "prompt": full_prompt, "stream": False}
        )
        try:
            answer = response.json().get("response", "No response")
            print("Jarvis:", answer)
            speak(answer)
        except:
            print("Jarvis (raw):", response.text)

# ---------------------- Main ----------------------
if __name__ == "__main__":
    documents = load_files()
    start_Jarvis()
    try:
        chat(documents)
    finally:
        stop_Jarvis()
