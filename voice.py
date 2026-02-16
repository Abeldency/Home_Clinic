# voice.py - Whisper-based Speech Recognition Helper (LOW MEMORY)

import whisper

# Tiny model = fastest + lowest RAM
model = whisper.load_model("tiny")

def recognize_audio(audio_path):
    try:
        result = model.transcribe(audio_path, fp16=False)
        text = result.get("text", "").strip()
        if text == "":
            return None
        return text.lower()
    except Exception as e:
        print("Whisper Error:", e)
        return None
