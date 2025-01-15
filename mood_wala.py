# Import dependencies
import speech_recognition as sr
import pyttsx3
from flask import Flask, request, jsonify
from transformers import pipeline
from googletrans import Translator
from textblob import TextBlob
import psycopg2

# Initialize Flask app
app = Flask(__name__)

# Initialize Speech Recognition
recognizer = sr.Recognizer()

# Initialize Translator
translator = Translator()

# Load Sentiment Analysis Model
sentiment_analyzer = pipeline("sentiment-analysis")

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Set to female voice
engine.setProperty('rate', 160)  # Adjust speed for better clarity

# Function to set voice properties based on mood
def set_mood_voice(mood):
    if mood == "POSITIVE":
        engine.setProperty('rate', 170)  # Cheerful tone
    elif mood == "NEGATIVE":
        engine.setProperty('rate', 140)  # Calming tone
        engine.setProperty('volume', 0.8)  # Softer volume
    else:
        engine.setProperty('rate', 160)  # Neutral tone

# Function to convert text to speech with mood-based tone
def speak(text, mood="NEUTRAL"):
    set_mood_voice(mood)
    engine.say(text)
    engine.runAndWait()

# Function to analyze the mood of the text
def analyze_mood(text):
    sentiment = sentiment_analyzer(text)[0]
    label = sentiment['label']
    if label == "NEGATIVE":
        return "NEGATIVE"
    elif label == "POSITIVE":
        return "POSITIVE"
    return "NEUTRAL"

# Function to interact with the PostgreSQL FAQ database
def get_faq_response(user_query, lang='en'):
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname="voice_query_vaman",
            user="postgrese",
            password="vaman",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Query the database for matching FAQ
        cursor.execute(
            "SELECT answer FROM faq WHERE question ILIKE %s AND language = %s LIMIT 1;",
            (f"%{user_query}%", lang)
        )
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the answer
        else:
            return "I'm sorry, I couldn't find an answer to that question."

    except Exception as e:
        print(f"Database error: {e}")
        return "There was an error connecting to the FAQ database."

    finally:
        if conn:
            cursor.close()
            conn.close()

# Flask route to handle text-based queries
@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    user_query = data.get("query", "")
    lang = data.get("language", "en")

    # Detect mood of the query
    mood = analyze_mood(user_query)

    # Fetch response from the FAQ database
    response = get_faq_response(user_query, lang)

    # Speak the response with mood-based tone
    speak(response, mood)
    return jsonify({"response": response, "mood": mood})

# Flask route to handle voice-based queries
@app.route('/voice', methods=['GET'])
def voice_interaction():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            # Convert speech to text
            query = recognizer.recognize_google(audio)
            print(f"You said: {query}")

            # Detect mood of the query
            mood = analyze_mood(query)

            # Fetch response from the FAQ database
            response = get_faq_response(query)

            # Speak the response
            speak(response, mood)
            return jsonify({"query": query, "response": response, "mood": mood})

        except sr.UnknownValueError:
            error_msg = "Sorry, I couldn't understand your query."
            speak(error_msg, "NEGATIVE")
            return jsonify({"error": error_msg})
        except sr.RequestError:
            error_msg = "Network error, please try again later."
            speak(error_msg, "NEGATIVE")
            return jsonify({"error": error_msg})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
