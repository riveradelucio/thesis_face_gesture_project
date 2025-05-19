import pyttsx3

def speak_text(text):
    engine = pyttsx3.init()

    # Force use of Microsoft Zira (English US Female)
    for voice in engine.getProperty('voices'):
        if "zira" in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 150)   # Adjust speaking speed
    engine.setProperty('volume', 1.0) # Set volume to maximum
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    print("🔊 Speaking with Microsoft Zira...")
    speak_text("Hello! This is a test of the offline text to speech system.")
