import os
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

evaluations = []
for file in os.listdir("evaluations"):
	evaluations.append(json.loads(open("evaluations/"+file, encoding="UTF-8").read()))

names = {}
try:
	names = json.loads(open("model_names.json", encoding="UTF-8").read())
except:
	pass

scores = {}
speeds = {}
combined = {}
models = []

for e in evaluations:
	model = e["model"]
	if model in names:
		model = names[e["model"]]
	models.append(model)

	speed_val = 0
	speed_len = 0
	local_scores = []
	for r in e["questions"]:
		for q in e["questions"][r]:
			question = e["questions"][r][q]

			local_scores.append(question["score"])

			speed_val += question["ttc"]
			speed_len += 1
	scores[model] = local_scores
	speeds[model] = speed_val / speed_len

speeds_normalized = {}

max_score = 0
for i in scores:
	if sum(scores[i]) > max_score:
		max_score = sum(scores[i])

max_speed = 0
for i in speeds:
	if speeds[i] > max_speed:
		max_speed = speeds[i]

for i in speeds:
	speeds_normalized[i] = speeds[i] / (max_speed)

for model in models:
	combined[model] = sum(scores[model]) / speeds_normalized[model]

# HEATMAP
plt.figure(figsize=(6,4))
sns.heatmap(
    pd.DataFrame.from_dict(scores, orient='index'),
    linewidths=.5,
    cmap='viridis',
    linecolor='white',
    cbar_kws={'label': 'Score'}
)
plt.title("LLM per-question score heatmap")
plt.tight_layout()
plt.show()

# SCORE GRAPH
sorted_list = pd.DataFrame.from_dict(scores, orient='index')
sorted_list.index.name = 'Model'
sorted_list.columns = [f'{i+1}' for i in range(sorted_list.shape[1])]
sorted_list = sorted_list.sum(axis=1).sort_values(ascending=False)

sns.barplot(
    x=sorted_list.values,
    y=sorted_list.index,
    palette="viridis"
)
plt.title('LLM benchmark scores')
plt.tight_layout()
plt.show()

# SPEED GRAPH
sorted_list = pd.DataFrame.from_dict(speeds, orient='index')
sorted_list.index.name = 'Model'
sorted_list.columns = [f'{i+1}' for i in range(sorted_list.shape[1])]
sorted_list = sorted_list.sum(axis=1).sort_values(ascending=True)

sns.barplot(
    x=sorted_list.values,
    y=sorted_list.index,
    palette="viridis"
)
plt.title('Time To Completion')
plt.tight_layout()
plt.show()

# FINAL GRAPH
sorted_list = pd.DataFrame.from_dict(combined, orient='index')
sorted_list.index.name = 'Model'
sorted_list.columns = [f'{i+1}' for i in range(sorted_list.shape[1])]
sorted_list = sorted_list.sum(axis=1).sort_values(ascending=False)

sns.barplot(
    x=sorted_list.values,
    y=sorted_list.index,
    palette="viridis"
)
plt.title('LLM final benchmark rankings')
plt.tight_layout()
plt.show()

# SCORE TO SPEED RATIO GRAPH
names = []
set_1 = []
set_2 = []

for model in models:
	names.append(model)
	set_1.append(sum(scores[model]))
	set_2.append((1 - speeds_normalized[model]) * max_score)

c = list(zip(names, set_1, set_2))
sorted_c = sorted(c, key=lambda t: t[1], reverse=False)
names, set_1, set_2 = zip(*sorted_c)

plt.figure(figsize=(7,4))

plt.plot(names, set_1,
	marker='o',
    color='tab:blue',
    linewidth=2,
    label="Benchmark Score"
)

plt.plot(names, set_2,
    marker='s',
    color='tab:red',
    linewidth=2,
    label="Speed"
)

plt.title("Score vs Speed")
plt.xticks(rotation=45, ha='right')
plt.xlabel('Model')
plt.grid(True, which='both', axis='y', linestyle='--', alpha=0.6)

plt.legend()

plt.tight_layout()
plt.show()