import requests
import speech_recognition as sr
import pyttsx3  # type: ignore
import os
import tempfile

# Initialize speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Configure pyttsx3 for a more human-like voice
voice = engine.getProperty('voices')[1]  # Use a female voice, if available
engine.setProperty('voice', voice.id)
engine.setProperty('rate', 150)  # Slow down the speech rate
engine.setProperty('volume', 0.9)  # Set volume level

# Flask server details
FLASK_SERVER_URL = "http://127.0.0.1:5000"

def play_audio_clip(audio_content):
    """
    Play audio content directly from a binary stream.
    """
    try:
        # Save the audio file temporarily
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_audio_file.write(audio_content)
        temp_audio_file.close()

        # Play the audio file
        if os.name == "nt":  # For Windows
            os.system(f"start {temp_audio_file.name}")
        else:  # For macOS or Linux
            os.system(f"mpg123 {temp_audio_file.name}")

        # Cleanup temporary file after playing
        os.remove(temp_audio_file.name)
    except Exception as e:
        print(f"Error playing audio clip: {e}")

def speak_text(text):
    """
    Use pyttsx3 to speak the given text with improved settings.
    """
    engine.say(text)
    engine.runAndWait()

def fetch_answer_from_server(question):
    """
    Send the question to the Flask server and fetch the answer.
    """
    try:
        response = requests.get(f"{FLASK_SERVER_URL}/query", params={"question": question}, stream=True)

        # Check if the response contains audio
        if response.headers.get('Content-Type') == 'audio/mpeg':
            print("Playing audio clip...")
            play_audio_clip(response.content)
            return None  # No text answer if audio is played

        # Handle text-based responses
        response_data = response.json()
        if response.status_code == 200:
            return response_data.get('answer', 'No answer available.')
        else:
            return response_data.get('error', 'Error fetching the answer.')
    except Exception as e:
        return f"Error communicating with the server: {e}"

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
            question = recognizer.recognize_google(audio)
            print(f"You asked: {question}")

            # Fetch the answer from the server
            answer = fetch_answer_from_server(question)

            # Speak the answer only if it's text
            if answer:
                print(f"Answer: {answer}")
                speak_text(answer)

        except sr.UnknownValueError:
            print("Sorry, I could not understand your speech.")
            speak_text("Sorry, I could not understand your speech.")
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")
            speak_text("There was an error with the speech recognition service.")

if __name__ == "__main__":
    main()
