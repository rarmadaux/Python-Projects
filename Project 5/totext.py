import whisper
import sounddevice as sd
import numpy as np

# Load the model once
model = whisper.load_model("small")

def listen_from_mic(duration=5, fs=16000):
    print(f"Listening for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    audio = np.squeeze(recording)
    result = model.transcribe(audio, fp16=False)
    return result["text"]

if __name__ == "__main__":
    text = listen_from_mic(duration=5)
    print("You said:", text)
