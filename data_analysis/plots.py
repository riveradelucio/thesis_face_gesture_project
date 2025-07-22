import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === CONFIGURATION ===
file_path = r"C:\Users\river\OneDrive - Radboud Universiteit\Documenten\GitHub\thesis_face_gesture_project\data_analysis\data_analysis.xlsx"
sheet_name = "Python"  # Change to the actual sheet name if different

# === LOAD DATA ===
df = pd.read_excel(file_path, sheet_name=sheet_name)

# === STEP 1: Compute mean scores per question
question_labels = [f"Q{i}" for i in range(1, 13)]

mean_scores = pd.DataFrame({
    'Question': question_labels,
    'System A Mean': [df[f"{q}_A"].mean() for q in question_labels],
    'System B Mean': [df[f"{q}_B"].mean() for q in question_labels]
})

# === BAR CHART ===
x = np.arange(len(mean_scores))
width = 0.35

fig_bar, ax_bar = plt.subplots()

# Bars
bar1 = ax_bar.bar(x - width/2, mean_scores['System A Mean'], width, label='System A')
bar2 = ax_bar.bar(x + width/2, mean_scores['System B Mean'], width, label='System B')

# Clear labels and title
ax_bar.set_ylabel('Average Godspeed Score')
ax_bar.set_title('Godspeed Questionnaire – Average Scores per Question (System A vs System B)')
ax_bar.set_xticks(x)
ax_bar.set_xticklabels(mean_scores['Question'])
ax_bar.legend()
plt.xticks(rotation=45)

# Add values above bars
for i in range(len(mean_scores)):
    ax_bar.text(x[i] - width/2, mean_scores['System A Mean'][i] + 0.05,
                f"{mean_scores['System A Mean'][i]:.2f}", ha='center', va='bottom', fontsize=8)
    ax_bar.text(x[i] + width/2, mean_scores['System B Mean'][i] + 0.05,
                f"{mean_scores['System B Mean'][i]:.2f}", ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig("godspeed_barplot.png", dpi=300)


# === RADAR PLOT SETUP ===
# Radar setup
labels = mean_scores['Question'].values
num_vars = len(labels)

# Angles for axes
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

# Values
values_a = mean_scores['System A Mean'].tolist() + [mean_scores['System A Mean'].tolist()[0]]
values_b = mean_scores['System B Mean'].tolist() + [mean_scores['System B Mean'].tolist()[0]]

# Create radar plot
fig, ax = plt.subplots(figsize=(9, 7), subplot_kw=dict(polar=True))

# Plot and fill
ax.plot(angles, values_a, label='System A', color='tab:blue', marker='o')
ax.fill(angles, values_a, alpha=0.2, color='tab:blue')

ax.plot(angles, values_b, label='System B', color='tab:orange', marker='o')
ax.fill(angles, values_b, alpha=0.2, color='tab:orange')

# Axis setup
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)
ax.set_ylim(0, 5)
ax.set_yticks([1, 2, 3, 4, 5])
ax.set_yticklabels(['1', '2', '3', '4', '5'])

# === Only annotate System B values ===
for i in range(num_vars):
    angle = angles[i]
    ax.text(angle, values_b[i] + 0.25, f"{values_b[i]:.2f}",
            color='tab:orange', fontsize=9, ha='center', va='center', fontweight='bold')

# Title and legend
ax.set_title('Godspeed Radar – Average Scores (System A vs System B)', pad=30)
ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.1))

plt.tight_layout()
plt.savefig("godspeed_radarplot.png", dpi=300)
plt.show()