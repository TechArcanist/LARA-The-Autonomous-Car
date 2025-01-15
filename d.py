import speech_recognition as sr

recognizer = sr.Recognizer()
with sr.Microphone() as source:
    print("Checking microphone...")
    recognizer.adjust_for_ambient_noise(source)
    audio = recognizer.listen(source, timeout=10)
    print("Microphone detected!")
