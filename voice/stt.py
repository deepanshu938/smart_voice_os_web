import os
import sys
from pathlib import Path
from typing import Optional

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

class SpeechToTextEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer() if HAS_SR else None
        if self.recognizer:
            # Dynamically adapt to room background noise
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 300
            self.recognizer.pause_threshold = 1.0

    def listen_and_transcribe(self) -> Optional[str]:
        """Listens from the default microphone and transcribes to text."""
        if not HAS_SR:
            print("[STT Warning]: speech_recognition library not installed. Using text input.")
            return None

        try:
            with sr.Microphone() as source:
                print("\n[Listening...] Speak now into your microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=15)
                print("[Processing speech...]")

            # Transcribe via Google Free Speech API
            text = self.recognizer.recognize_google(audio)
            print(f"[You said]: {text}")
            return text

        except sr.WaitTimeoutError:
            print("[STT]: No speech detected within timeout.")
            return None
        except sr.UnknownValueError:
            print("[STT]: Could not understand audio.")
            return None
        except Exception as e:
            print(f"[STT Error]: {str(e)}")
            return None
