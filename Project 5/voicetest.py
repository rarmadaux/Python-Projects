#import pyttsx3

#engine = pyttsx3.init()
#engine.say("Hello! I am your assistant. Your ip is 192.168.1.1")
#engine.runAndWait()

from gtts import gTTS
import pygame
import time

def speak(text):
    tts = gTTS(text=text, lang="en")
    tts.save("reply.mp3")
    
    pygame.mixer.init()
    pygame.mixer.music.load("reply.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

# Test
speak("Hello! I am your assistant with a human voice.")
