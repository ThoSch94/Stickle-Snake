
"""
Distance Analysis Script for 2D Morphological Stickleback Data

This script analyzes distance measurements from landmarks, computing statistical
summaries and creating visualizations including boxplots, scatterplots, and
histograms for distribution analysis.

The input CSV should have columns: 'Landmark' and 'Distance', and optionally 'Image' for identifying outliers.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import argparse

# Calculate descriptive statistics
def calculate_statistics(data):
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
    if 'Image' in data.columns:
        max_distance_images = data.loc[data.groupby('Landmark')['Distance'].idxmax(), ['Landmark', 'Image']]
        max_distance_images.rename(columns={'Image': 'worst_outlier_image'}, inplace=True)
        stats = stats.merge(max_distance_images, on='Landmark')

    print("Statistical Data per Landmark:")
    print(stats)

    return stats

# Generate LaTeX table for report/publication
def generate_latex_table(stats):
    """
    Convert statistics DataFrame to LaTeX table format for use in documents.
    """
    latex_table = tabulate(stats, headers='keys', tablefmt='latex', numalign="right")
    print("\nSaved LaTeX Table as results_table.tex\n")
    with open('data/output/results_table.tex', 'w') as tf:
     tf.write(latex_table)
    return latex_table

def visualize_data_boxplot(data):  
    """
    Visualize the distribution and outliers of distances for each landmark.
    Shows median, quartiles, and outliers in a compact format.
    """
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="Landmark", y="Distance", data=data, palette="vlag")
    plt.title("Distribution of Distances per Landmark")
    plt.xlabel("Landmark")
    plt.ylabel("Distance")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('data/output/boxplot_distances.pdf')
    #plt.show()

def visualize_data_scatterplot(data):
    """Display each distance measurement as a point, colored by landmark.   
    Scatterplot: Individual distance points colored by landmark
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
    plt.title("Scatterplot of Distances per Landmark")
    plt.xlabel("Landmark")
    plt.ylabel("Distance")
    plt.xticks(rotation=45)
    plt.legend(title="Landmark")
    plt.tight_layout()
    plt.savefig('data/output/scatterplot_distances.pdf')
    #plt.show()

def visualize_data_outliers(data):
    """
    Visualize the distribution and outliers of distances for each landmark.
Shows median, quartiles, and outliers in a compact format.
    """
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="Landmark", y="Distance", data=data, palette="vlag")
    plt.title("Visualization of Distances per Landmark")
    plt.xlabel("Landmark")
    plt.ylabel("Distance")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('data/output/outliers_boxplot.pdf')
    #plt.show()

def visualize_data_histograms(data):
    """
    Create a grid of histograms (one per landmark) with density curves.
    Each subplot shows the frequency distribution of distances for a single landmark.
    """
    landmarks = data['Landmark'].unique()
    num_landmarks = len(landmarks)

    #Error checking for empty dataset
    if num_landmarks == 0:
        print("No landmarks found in the dataset. Please check the input CSV.")
        return

    fig, axes = plt.subplots(nrows=(num_landmarks + 2) // 3, ncols=3, figsize=(15, 5 * (num_landmarks // 3 + 1)))
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
        axes[i].set_xlabel("Distance")
        axes[i].set_ylabel("Frequency")

    # Remove empty subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.savefig('data/output/histograms_distances.pdf')
    # plt.show()

def main(input_csv="data/output/landmark_distances.csv", visualize_boxplot=False, visualize_scatterplot=False, visualize_histograms=False, visualize_error_analysis=False, latex_table=False, all_visualizations=False):

    data = pd.read_csv(
        input_csv,
        delimiter=",",
        na_values=["", " ", "None", "NaN", "nan"]
    )

    print("Loaded Data:")
    print(data.head())


    stats = calculate_statistics(data)

    #flags to output different visualizations
    if visualize_boxplot:
        print("\nVisualizing boxplot of distances...\n")
        visualize_data_boxplot(data)
    if visualize_scatterplot:
        print("\nVisualizing scatterplot of distances...\n")
        visualize_data_scatterplot(data)
    if visualize_histograms:
        print("\nVisualizing histograms of distances...\n")
        visualize_data_histograms(data)
    if visualize_error_analysis:
        print("\nVisualizing outliers in the data...\n")
        visualize_data_outliers(data)
    if latex_table:
        print("\nGenerating LaTeX table...\n")
        generate_latex_table(stats)

    if all_visualizations:
        print("\nGenerating all visualizations...\n")
        visualize_data_boxplot(data)
        visualize_data_scatterplot(data)
        visualize_data_histograms(data)
        visualize_data_outliers(data)
        latex_table = generate_latex_table(stats)

    
    #print(data)
    # Placeholder for any additional analysis or function calls
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Further analysis of landmark distance data.")
    parser.add_argument("--input_csv", type=str, default="data/output/landmark_distances.csv", help="Path to the input CSV file containing landmark distances.")
    parser.add_argument("--visualize_boxplot", action="store_true", help="Flag to visualize boxplot of distances.")
    parser.add_argument("--visualize_scatterplot", action="store_true", help="Flag to visualize scatterplot of distances.")
    parser.add_argument("--visualize_histograms", action="store_true", help="Flag to visualize histograms of distances.")
    parser.add_argument("--visualize_error_analysis", action="store_true", help="Flag to visualize outliers in the data.")
    parser.add_argument("--latex_table", action="store_true", help="Flag to generate LaTeX table of statistics.")
    parser.add_argument("--all_visualizations", action="store_true", help="Flag to generate all visualizations (boxplot, scatterplot, histograms, error analysis).")
    args = parser.parse_args()

    main(input_csv=args.input_csv, all_visualizations=args.all_visualizations, visualize_boxplot=args.visualize_boxplot, visualize_scatterplot=args.visualize_scatterplot, visualize_histograms=args.visualize_histograms, visualize_error_analysis=args.visualize_error_analysis, latex_table=args.latex_table)