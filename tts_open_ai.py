import openai

openai.api_key = "your-whisper-api-key"

def speech_to_text(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]
