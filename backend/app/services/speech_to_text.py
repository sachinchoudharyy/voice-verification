import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
import tempfile
import os

SAMPLE_RATE = 48000

def transcribe_audio(audio_bytes: bytes) -> str | None:
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        write(f.name, SAMPLE_RATE, audio_np)
        temp_path = f.name

    r = sr.Recognizer()
    with sr.AudioFile(temp_path) as source:
        audio = r.record(source)

    os.unlink(temp_path)

    try:
        return r.recognize_google(audio)
    except:
        return None
