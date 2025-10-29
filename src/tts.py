"""Simple offline TTS using pyttsx3. Produces WAV files per slide.
"""
import pyttsx3
import os


def synthesize_texts(texts, out_dir: str, voice_rate: int = 150):
    os.makedirs(out_dir, exist_ok=True)
    engine = pyttsx3.init()
    engine.setProperty('rate', voice_rate)
    # choose voice if available
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)

    out_files = []
    for i, t in enumerate(texts, start=1):
        out_path = os.path.join(out_dir, f'slide_{i:02d}.mp3')
        engine.save_to_file(t or '', out_path)
        out_files.append(out_path)
    engine.runAndWait()
    return out_files