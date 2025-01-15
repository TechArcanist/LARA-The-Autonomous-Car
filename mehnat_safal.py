import os
import wave
import numpy as np
from vosk import Model, KaldiRecognizer
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import requests
from pydub import AudioSegment

# Set up constants
MODEL_PATH = r"C:\Users\TUF\vosk-model-en-in-0.5\vosk-model-en-in-0.5"  # Path to VOSK model
FAQ_PATH = r"C:\Users\TUF\mehnat_2.0\Greetings.csv"  # Path to FAQ dataset
TTS_API_KEY = "your-eleven-labs-api-key"  # Eleven Labs API key

# Ensure model directory exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model path '{MODEL_PATH}' does not exist.")

# Load the VOSK speech recognition model
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)  # 16 kHz sampling rate

# Load the Hugging Face Transformer model for NLU
xlm_model_name = "xlm-roberta-base"
tokenizer = AutoTokenizer.from_pretrained(xlm_model_name)
# nlu_model = AutoModelForSeq2SeqLM.from_pretrained(xlm_model_name)
nlu_model = AutoModelForSequenceClassification.from_pretrained(xlm_model_name)
nlu_pipeline = pipeline("text2text-generation", model=nlu_model, tokenizer=tokenizer)

# Load and preprocess the FAQ dataset
def load_faq_dataset(faq_path):
    import pandas as pd

    if not os.path.exists(faq_path):
        raise FileNotFoundError(f"FAQ dataset '{faq_path}' does not exist.")

    df = pd.read_csv(faq_path)
    if "Question" not in df.columns or "Answer" not in df.columns:
        raise ValueError("Dataset must contain 'Question' and 'Answer' columns.")

    questions = df["Question"].tolist()
    answers = df["Answer"].tolist()
    return questions, answers

faq_questions, faq_answers = load_faq_dataset(FAQ_PATH)
import sounddevice as sd
from scipy.io.wavfile import write

def record_audio(output_path, duration=5, sample_rate=44100):
    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()  # Wait until recording is finished
    write(output_path, sample_rate, audio)
    print(f"Recording saved to {output_path}")

record_audio("user_query.wav")


# Speech-to-Text Function
def speech_to_text(audio_path):
    
    # Convert audio to required format
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    temp_path = "temp_audio.wav"
    audio.export(temp_path, format="wav")

    # Process audio with VOSK
    wf = wave.open(temp_path, "rb")
    transcript = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            transcript += eval(result).get("text", "") + " "
    return transcript.strip()

# FAQ Response Function
def get_faq_response(question):
    encoded_inputs = tokenizer(question, return_tensors="pt")
    outputs = nlu_model.generate(**encoded_inputs)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Find the closest match from the FAQ dataset (simplistic matching)
    for faq_question, faq_answer in zip(faq_questions, faq_answers):
        if faq_question.lower() in generated_text.lower():
            return faq_answer
    return "Sorry, I couldn't find an answer to that question."

# Text-to-Speech Function
def text_to_speech(text, output_path="response_audio.mp3"):
    url = "https://api.elevenlabs.io/v1/text-to-speech"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": TTS_API_KEY
    }
    payload = {
        "text": text,
        "voice": "en_us_male"  # You can customize the voice if required
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Audio response saved to {output_path}")
    else:
        print("Failed to synthesize speech. API response:", response.text)

# Main Interaction Function
def interact_with_user(audio_input_path):
    print("Processing user input...")
    question = speech_to_text(audio_input_path)
    print(f"Recognized Question: {question}")

    response = get_faq_response(question)
    print(f"Generated Response: {response}")

    text_to_speech(response)

# Example Usage
if __name__ == "__main__":
    user_audio_path = "user_query.wav"  # Replace with the path to your input audio file
    interact_with_user(user_audio_path)
