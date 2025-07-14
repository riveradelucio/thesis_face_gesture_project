from pydub import AudioSegment
import os

# Full path to your .ogg file
input_path = r"C:\Users\river\OneDrive - Radboud Universiteit\Bureaublad\Desktop\Master\Thesis\Evaluation\Participants\Responses\ID_003\System A\ID_003_Interview.ogg"

# Output file path — will save as .wav in the same folder
output_path = os.path.splitext(input_path)[0] + ".wav"

# Load and convert
audio = AudioSegment.from_ogg(input_path)
audio.export(output_path, format="wav")

print(f"✅ Done! Converted file saved at:\n{output_path}")
