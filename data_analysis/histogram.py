import pandas as pd
import matplotlib.pyplot as plt

# ✅ Load the Excel sheet
file_path = r"C:\Users\river\OneDrive - Radboud Universiteit\Documenten\GitHub\thesis_face_gesture_project\data_analysis\data_analysis.xlsx"
sheet_name = "Accuracy"

df = pd.read_excel(file_path, sheet_name=sheet_name)

# ✅ Ensure System B Accuracy exists
if 'System B Accuracy' not in df.columns:
    df['System B Accuracy'] = df['System B Successes'] / df['System B Attempts']

# ✅ Divide into low and high performers
threshold = 0.60
high_performers = df[df['System B Accuracy'] >= threshold]
low_performers = df[df['System B Accuracy'] < threshold]

# ✅ Print summary
print("🎯 High Performers (≥ 60%):")
print(high_performers[['Participant Number', 'System B Accuracy']])

print("\n⚠️ Low Performers (< 60%):")
print(low_performers[['Participant Number', 'System B Accuracy']])

print(f"\n📊 Count Summary:")
print(f"High performers: {len(high_performers)}")
print(f"Low performers: {len(low_performers)}")

# ✅ Create histogram
plt.figure(figsize=(8, 5))
bins = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
plt.hist(df['System B Accuracy'], bins=bins, edgecolor='black', color='skyblue')

# ✅ Threshold line
plt.axvline(threshold, color='orange', linestyle='--', label='60% Threshold')
plt.xlabel('System B Accuracy')
plt.ylabel('Number of Participants')
plt.title('Distribution of System B Accuracy Across Participants')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)

# ✅ Save histogram
plt.tight_layout()
plt.savefig("system_b_accuracy_histogram.png", dpi=300)
plt.show()
