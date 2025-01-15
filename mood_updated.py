import psycopg2
import speech_recognition as sr
import pyttsx3
import requests
import librosa
import numpy as np
import wave
import json

# Initialize the recognizer for speech recognition
recognizer = sr.Recognizer()

# Initialize pyttsx3 engine for text-to-speech
engine = pyttsx3.init()

# Set a female, human-like voice for the response
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice
engine.setProperty('rate', 150)  # Normal speed
engine.setProperty('volume', 1)  # Max volume

# Connect to the PostgreSQL database
def connect_to_db():
    try:
        connection = psycopg2.connect(
            host="localhost",  # Database server
            database="voice_query_vaman",  # Your database name
            user="postgres",  # Your username
            password="vaman",  # Your password
            port="5432"  # Default PostgreSQL port
        )
        return connection
    except Exception as error:
        print(f"Error connecting to database: {error}")
        return None

# Fetch query from the database
def fetch_query_from_db(query):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT answer, language FROM quer WHERE question = %s;", (query,))  # Fetch answer
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if result:
            return result  # Answer and language
        else:
            return None
    return None

# Function to fetch answer from Gemini API if not found in DB
def fetch_from_gemini(query):
    # Replace with actual API endpoint and key if available
    url = "https://api.gemini.com/v1/query-answer"
    params = {
        "query": query,
        "language": "en"  # Default language, can be changed dynamically
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()["answer"]
    else:
        return "Sorry, I could not find an answer."

# Update the database with the new question-answer pair
def update_db(query, answer, language, category="General"):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO quer (question, answer, language, category) VALUES (%s, %s, %s, %s);",
            (query, answer, language, category)
        )
        connection.commit()
        cursor.close()
        connection.close()

# Function to speak out a response with a given mood
def speak(text, language):
    engine.setProperty('rate', 150)  # Reset to normal speed
    engine.setProperty('volume', 1)  # Max volume
    engine.say(text)
    engine.runAndWait()

# Function to detect language and tone of voice (Basic)
def detect_language_and_tone(audio_data):
    # Save audio data to a temporary WAV file
    with wave.open("temp_audio.wav", "wb") as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(16000)  # 16 kHz sample rate
        wf.writeframes(audio_data.get_wav_data())  # Write audio data to file

    # Analyze audio for language detection (based on pitch or other features)
    try:
        y, sr = librosa.load("temp_audio.wav", sr=None)  # Load the audio using librosa
        pitch, mag = librosa.core.piptrack(y=y, sr=sr)
        pitch_values = pitch[pitch > 0]
        average_pitch = np.mean(pitch_values)

        if average_pitch > 200:  # If the pitch is high, it's likely Hindi
            return "Hindi"
        else:
            return "English"
    except Exception as e:
        print("Error analyzing audio:", e)
        return "English"

# Function to listen for a query
def listen_for_query():
    with sr.Microphone() as source:
        print("Listening for query...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=20, phrase_time_limit=30)

        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio)
            print(f"Recognized query: {query}")
            return query, audio
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the audio.")
            return None, None
        except sr.RequestError:
            print("Request error.")
            return None, None

# Main function
if __name__ == "__main__":
    query, audio = listen_for_query()
    if query:
        # Detect the language of the voice input
        language = detect_language_and_tone(audio)
        print(f"Detected language: {language}")

        # Fetch query from the database
        result = fetch_query_from_db(query)
        if result:
            # If query found, speak the answer
            answer, lang = result
            speak(answer, lang)
        else:
            # If query not found, fetch answer from Gemini API
            answer = fetch_from_gemini(query)
            print(f"Answer from Gemini: {answer}")

            # Update the database with the new query-answer pair
            update_db(query, answer, language)
            speak(f"Answer updated in the database. Here's the response: {answer}")
    else:
        print("No query recognized.")
