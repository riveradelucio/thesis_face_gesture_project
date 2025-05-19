import pyttsx3

# Initialize the text-to-speech engine once
_engine = pyttsx3.init()

# Select the preferred voice (Microsoft Zira - US English Female)
for voice in _engine.getProperty('voices'):
    if "zira" in voice.id.lower():
        _engine.setProperty('voice', voice.id)
        break

# Set standard speech properties
_engine.setProperty('rate', 150)    # Speed
_engine.setProperty('volume', 1.0)  # Max volume

def speak_text(text: str) -> None:
    """
    Speak the given text out loud using the TTS engine.

    Args:
        text (str): The message to be spoken.
    """
    _engine.say(text)
    _engine.runAndWait()

# Optional test when running this file directly
if __name__ == "__main__":
    print("🔊 Speaking with Microsoft Zira...")
    speak_text("Hello! This is a test of the offline text to speech system.")
