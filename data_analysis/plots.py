import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Mean scores for questions (from previous results)
mean_scores = pd.DataFrame({
    'Question': ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12'],
    'System A Mean': [3.090909, 2.272727, 2.818182, 2.909091, 2.909091, 2.636364,
                      2.818182, 3.454545, 2.909091, 2.727273, 2.545455, 2.545455],
    'System B Mean': [3.454545, 2.909091, 3.272727, 3.363636, 3.454545, 3.909091,
                      3.545455, 4.272727, 3.909091, 3.636364, 3.181818, 3.000000]
})

# --- BAR CHART ---
x = np.arange(len(mean_scores))
width = 0.35

fig_bar, ax_bar = plt.subplots()
bar1 = ax_bar.bar(x - width/2, mean_scores['System A Mean'], width, label='System A')
bar2 = ax_bar.bar(x + width/2, mean_scores['System B Mean'], width, label='System B')

ax_bar.set_ylabel('Mean Score')
ax_bar.set_title('Godspeed Questionnaire – System A vs System B')
ax_bar.set_xticks(x)
ax_bar.set_xticklabels(mean_scores['Question'])
ax_bar.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# --- RADAR PLOT ---
# Radar plots need circular layout and categories
labels = mean_scores['Question'].values
num_vars = len(labels)

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
values_a = mean_scores['System A Mean'].tolist()
values_b = mean_scores['System B Mean'].tolist()

# Repeat first value to close the circular graph
values_a += values_a[:1]
values_b += values_b[:1]
angles += angles[:1]

fig_radar, ax_radar = plt.subplots(subplot_kw={'polar': True})
ax_radar.plot(angles, values_a, label='System A')
ax_radar.fill(angles, values_a, alpha=0.25)
ax_radar.plot(angles, values_b, label='System B')
ax_radar.fill(angles, values_b, alpha=0.25)
ax_radar.set_xticks(angles[:-1])
ax_radar.set_xticklabels(labels)
ax_radar.set_title('Godspeed Radar Plot: System A vs System B')
ax_radar.legend(loc='upper right')

plt.tight_layout()
plt.show()
