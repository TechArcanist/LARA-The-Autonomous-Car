import requests
import speech_recognition as sr
import pyttsx3 # type: ignore

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
        # Send the question to the Flask server
        response = requests.get(FLASK_SERVER_URL, params={"question": question})
        response_data = response.json()

        # Check for a valid response
        if response.status_code == 200:
            answer = response_data.get('answer', 'No answer available.')
            print(f"Answer: {answer}")
            return answer
        else:
            error_message = response_data.get('error', 'Error fetching the answer.')
            print(f"Error: {error_message}")
            return error_message
    except Exception as e:
        print(f"Error communicating with the server: {e}")
        return "There was an error communicating with the server."

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
            speak_text(answer)

        except sr.UnknownValueError:
            print("Sorry, I could not understand your speech.")
            speak_text("Sorry, I could not understand your speech.")
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")
            speak_text("There was an error with the speech recognition service.")

if __name__ == "__main__":
    main()
