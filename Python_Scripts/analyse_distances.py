"""
Distance Analysis Script for 2D Morphological Stickleback Data

This script analyzes distance measurements from landmarks, computing statistical
summaries and creating visualizations including boxplots, scatterplots, and
histograms for distribution analysis.

The input CSV should have columns: 'Landmark' and 'Distance'
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# Load and prepare data
distances_csv = "Canad_Zoo_Training/landmark_distances.csv"

data = pd.read_csv(
    distances_csv,
    delimiter=",",
    na_values=["", " ", "None", "NaN", "nan"]
)

print(data)

# Calculate descriptive statistics
"""
Group distances by landmark and compute statistical measures.
Returns a DataFrame with mean, median, std, min, and max for each landmark.
"""
stats = data.groupby('Landmark')['Distance'].agg([
    ('mean', 'mean'),
    ('median', 'median'),
    ('std', 'std'),
    ('min', 'min'),
    ('max', 'max')
]).reset_index()


# Add the image name for the max distance per landmark
max_distance_images = data.loc[data.groupby('Landmark')['Distance'].idxmax(), ['Landmark', 'Image']]
max_distance_images.rename(columns={'Image': 'worst_outlier_image'}, inplace=True)
stats = stats.merge(max_distance_images, on='Landmark')

print("Statistische Kennzahlen pro Landmarke:")
print(stats)

# Generate LaTeX table for report/publication
"""
Convert statistics DataFrame to LaTeX table format for use in documents.
"""
#latex_table = tabulate(stats, headers='keys', tablefmt='latex', numalign="right")
#print("\nLaTeX-Tabelle:")
#print(latex_table)

# Set visualization style
#sns.set(style="whitegrid")

# Boxplot: Distribution of distances per landmark
"""
Visualize the distribution and outliers of distances for each landmark.
Shows median, quartiles, and outliers in a compact format.
"""
plt.figure(figsize=(12, 6))
sns.boxplot(x="Landmark", y="Distance", data=data, palette="vlag")
plt.title("Verteilung der Abstände pro Landmarke")
plt.xlabel("Landmarke")
plt.ylabel("Abstand")
plt.xticks(rotation=45)
plt.tight_layout()
#plt.show()

# Scatterplot: Individual distance points colored by landmark
"""
Display each distance measurement as a point, colored by landmark.
Useful for identifying individual data points and potential clusters.
"""
plt.figure(figsize=(12, 6))
sns.scatterplot(
    x="Landmark", 
    y="Distance", 
    hue="Landmark", 
    palette=["black"] * data['Landmark'].nunique(), 
    data=data,
    legend="full",
    s=50
)
plt.title("Scatterplot der Abstände pro Landmarke")
plt.xlabel("Landmarke")
plt.ylabel("Abstand")
plt.xticks(rotation=45)
plt.legend(title="Landmarke")
plt.tight_layout()
#plt.show()

# Histograms: Distribution histograms for each landmark
"""
Create a grid of histograms (one per landmark) with density curves.
Each subplot shows the frequency distribution of distances for a single landmark.
"""
landmarks = data['Landmark'].unique()
num_landmarks = len(landmarks)

fig, axes = plt.subplots(nrows=num_landmarks // 3 + 1, ncols=3, figsize=(15, 5 * (num_landmarks // 3 + 1)))
axes = axes.flatten()

for i, landmark in enumerate(landmarks):
    sns.histplot(
        data[data['Landmark'] == landmark]['Distance'],
        ax=axes[i],
        kde=True,
        bins=20,
        color="blue"
    )
    axes[i].set_title(f"Landmark {landmark}")
    axes[i].set_xlabel("Abstand")
    axes[i].set_ylabel("Häufigkeit")

# Remove empty subplots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
#plt.show()