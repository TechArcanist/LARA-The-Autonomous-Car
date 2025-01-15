import requests
import speech_recognition as sr
import pyttsx3  # type: ignore

# Initialize speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Flask server details
FLASK_SERVER_URL = "http://127.0.0.1:5000"

def speak_text(text):
    """
    Use pyttsx3 to speak the given text.
    """
    engine.say(text)
    engine.runAndWait()

def fetch_answer_from_server(question):
    """
    Send the question to the Flask server and fetch the answer.
    """
    try:
        response = requests.get(f"{FLASK_SERVER_URL}/query", params={"question": question})
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

            # Speak the answer
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
