import os
import sounddevice as sd
from vosk import Model,KaldiRecognizer
import json

MODEL_PATH = r"C:\Users\TUF\vosk-model-en-in-0.5\vosk-model-en-in-0.5"  # Replace with the actual model path
if not os.path.exists(MODEL_PATH):
    print("Model not found! Please download it from https://alphacephei.com/vosk/models and extract it.")
    exit(1)

model = Model(MODEL_PATH)
def recognize_speech():
    # Configure the recognizer
    recognizer = KaldiRecognizer(model, 16000)  # 16kHz sample rate
    
    # Capture audio from the microphone
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=lambda indata, frames, time, status: None):
        print("Listening... Press Ctrl+C to stop.")
        
        while True:
            data = sd.rec(int(16000 * 1), samplerate=16000, channels=1, dtype='int16')  # Record 1 second chunks
            sd.wait()  # Wait until recording is finished
            
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                print("Recognized text:", result['text'])
            else:
                print("Partial result:", recognizer.PartialResult())

if __name__ == "__main__":
    try:
        recognize_speech()
    except KeyboardInterrupt:
        print("\nExiting...")

