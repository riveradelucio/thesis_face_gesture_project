import pandas as pd
from scipy.stats import ttest_rel

# ✅ Step 1: Load your Excel file
file_path = r"C:\Users\river\OneDrive - Radboud Universiteit\Documenten\GitHub\thesis_face_gesture_project\data_analysis\data_analysis.xlsx"
df = pd.read_excel(file_path)

# ✅ Step 2: Drop the first column if needed (participant ID)
df = df.drop(columns=["Participant Number"])

# ✅ Step 3: Get System A and B columns
system_a = df[[col for col in df.columns if col.endswith('_A')]]
system_b = df[[col for col in df.columns if col.endswith('_B')]]

# ✅ Step 4: Print mean scores per question
mean_scores = pd.DataFrame({
    'System A Mean': system_a.mean(),
    'System B Mean': system_b.mean()
})
print("Mean scores per question:\n")
print(mean_scores)

# ✅ Step 5: Run paired t-test for each question
print("\nPaired t-test results per question:")
for col_a in system_a.columns:
    col_b = col_a.replace('_A', '_B')
    t_stat, p_val = ttest_rel(df[col_a], df[col_b])
    print(f"{col_a.replace('_A', '')}: t = {t_stat:.2f}, p = {p_val:.4f}")
