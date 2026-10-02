import asyncio
import os
import tempfile
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import VOICE_NAME, VOICE_RATE

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class TextToSpeechEngine:
    def __init__(self, voice: str = VOICE_NAME, rate: str = VOICE_RATE):
        self.voice = voice
        self.rate = rate
        if HAS_PYGAME:
            try:
                pygame.mixer.init()
            except Exception:
                pass

    async def _generate_audio_file(self, text: str, output_path: str):
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await communicate.save(output_path)

    def speak(self, text: str):
        """Speaks the text aloud using Microsoft Edge Neural TTS."""
        if not text.strip():
            return
            
        print(f"\n[Aura Speaking]: {text}\n")
        
        if not HAS_EDGE_TTS:
            # Fallback print if edge-tts not installed
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_path = temp_audio.name

        try:
            # Run async edge_tts generation
            asyncio.run(self._generate_audio_file(text, temp_path))

            # Playback audio
            if HAS_PYGAME and pygame.mixer.get_init():
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.music.unload()
            else:
                # Windows built-in media playback fallback
                os.system(f'powershell -c "(New-Object Media.SoundPlayer \'{temp_path}\').PlaySync();" >$null 2>&1')
        except Exception as e:
            # Non-blocking error logging
            pass
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
