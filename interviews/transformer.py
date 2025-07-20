import subprocess
import os

# === USER INPUT HERE ===
participant_id = "ID_016"  # e.g. ID_003
system = "B"               # "A" or "B"

# === AUTO-GENERATED PATH AND FILENAMES ===
base_dir = fr"C:\Users\river\OneDrive - Radboud Universiteit\Bureaublad\Desktop\Master\Thesis\Evaluation\Participants\Responses"
input_filename = f"{participant_id}_{system}_Interview.ogg"
output_filename = f"{participant_id}_{system}_Interview_word_ready.wav"
folder_path = os.path.join(base_dir, participant_id, f"System_{system}")

# Full paths
input_path = os.path.join(folder_path, input_filename)
output_path = os.path.join(folder_path, output_filename)

# === FFMPEG CONVERSION ===
command = [
    "ffmpeg",
    "-i", input_path,
    "-acodec", "pcm_s16le",  # WAV PCM 16-bit
    "-ac", "1",              # Mono
    "-ar", "16000",          # 16 kHz sample rate
    output_path
]

print(f"🔄 Converting:\nFrom: {input_path}\nTo:   {output_path}")
subprocess.run(command)
print("✅ Done! Word-compatible file created.")
