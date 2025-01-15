import requests
import speech_recognition as sr
import pyttsx3  # type: ignore
from googletrans import Translator

# Initialize speech recognizer, text-to-speech engine, and translator
recognizer = sr.Recognizer()
engine = pyttsx3.init()
translator = Translator()

# Configure pyttsx3 for a more human-like voice (Hindi-compatible if available)
voices = engine.getProperty('voices')
for voice in voices:
    if "hindi" in voice.languages:
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 150)  # Slow down the speech rate (default is around 200)
engine.setProperty('volume', 0.9)  # Set volume level (0.0 to 1.0)

# Flask server details
FLASK_SERVER_URL = "http://127.0.0.1:5000"

def speak_text(text, language='en'):
    """
    Speak the given text using pyttsx3 in the specified language.
    """
    if language == 'hi':
        engine.setProperty('voice', voices[0].id)  # Ensure Hindi TTS is selected
    else:
        engine.setProperty('voice', voices[1].id)  # Switch to the default English voice
    
    engine.say(text)
    engine.runAndWait()

def fetch_answer_from_server(question, language='en'):
    """
    Send the question to the Flask server and fetch the answer.
    Translate question to English for server query and translate response back to Hindi if needed.
    """
    try:
        # Translate question to English if it is in Hindi
        if language == 'hi':
            translated_question = translator.translate(question, src='hi', dest='en').text
        else:
            translated_question = question

        response = requests.get(f"{FLASK_SERVER_URL}/query", params={"question": translated_question})
        response_data = response.json()

        if response.status_code == 200:
            answer = response_data.get('answer', 'No answer available.')
            # Translate answer back to Hindi if needed
            if language == 'hi':
                answer = translator.translate(answer, src='en', dest='hi').text
            return answer
        else:
            return response_data.get('error', 'Error fetching the answer.')
    except Exception as e:
        return f"Error communicating with the server: {e}"

def detect_language(text):
    """
    Detect the language of the input text.
    """
    detected_lang = translator.detect(text).lang
    return detected_lang

def main():
    """
    Main function to capture speech, process it, and fetch the answer.
    """
    with sr.Microphone() as source:
        print("Say your question:")
        try:
            # Capture voice input
            audio = recognizer.listen(source)

            # Convert speech to text
            question = recognizer.recognize_google(audio, language="hi-IN")
            print(f"You asked: {question}")

            # Detect language (Hindi or English)
            language = detect_language(question)
            print(f"Detected language: {language}")

            # Fetch the answer from the server
            answer = fetch_answer_from_server(question, language)

            # Speak the answer
            print(f"Answer: {answer}")
            speak_text(answer, language)

        except sr.UnknownValueError:
            print("Sorry, I could not understand your speech.")
            speak_text("Sorry, I could not understand your speech.", language='en')
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")
            speak_text("There was an error with the speech recognition service.", language='en')

if __name__ == "__main__":
    main()
