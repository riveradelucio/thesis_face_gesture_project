import pandas as pd
from scipy.stats import ttest_rel
import matplotlib.pyplot as plt

# ✅ Step 1: Load the Excel sheet
file_path = r"C:\Users\river\OneDrive - Radboud Universiteit\Documenten\GitHub\thesis_face_gesture_project\data_analysis\data_analysis.xlsx"
sheet_name = "Accuracy"

df = pd.read_excel(file_path, sheet_name=sheet_name)

# ✅ Step 2: Recalculate accuracies (for validation)
df['System A Accuracy (Check)'] = df['System A Successes'] / df['System A Attempts']
df['System B Accuracy (Check)'] = df['System B Successes'] / df['System B Attempts']

# ✅ Step 3: Show participant accuracy
print("\n🎯 Participant Accuracies:")
print(df[['Participant Number', 'System A Accuracy', 'System B Accuracy']])

# ✅ Step 4: Average accuracy
avg_a = df['System A Accuracy'].mean()
avg_b = df['System B Accuracy'].mean()

print("\n📈 Average Accuracies:")
print(f"System A (Motion-based): {avg_a:.2%}")
print(f"System B (With Recognition): {avg_b:.2%}")

# ✅ Step 5: Paired T-test
t_stat, p_val = ttest_rel(df['System A Accuracy'], df['System B Accuracy'])
print("\n🔬 Paired T-Test:")
print(f"T-statistic: {t_stat:.3f}")
print(f"P-value    : {p_val:.4f}")
if p_val < 0.05:
    print("🟢 Statistically significant difference.")
else:
    print("🔵 No statistically significant difference.")

# ✅ Step 6: (Optional) Plot comparison
df.plot(x='Participant Number', y=['System A Accuracy', 'System B Accuracy'], kind='bar')
plt.title("System Accuracy per Participant")
plt.ylabel("Accuracy")
plt.ylim(0, 1)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
