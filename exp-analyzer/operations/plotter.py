# this is an example to plot the results.
import os
import json
from itertools import combinations
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def read_results(directory):
    results = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as f:
                data = json.load(f)
                if not 'info' in data: continue
                domain_instance = f"{data['info']['domain']}_{data['info']['problem']}"
                results.append((data['info']['q'], data['info']['k'], data['info']['tag'], domain_instance, data['diversity-scores']['behaviour-count']))
    return results

def plot_planners(q, kvalues, planners, dumpfig):
    k_v_sorted = sorted(kvalues)
    planners_names = None
    data = []
    
    planner_1_name = None
    planner_1_mean = []
    planner_1_std = []
    planner_2_name = None
    planner_2_mean = []
    planner_2_std = []

    for k in k_v_sorted:
        if k not in planners: continue
        planner1 = planners[k]['planner1']
        planner2 = planners[k]['planner2']

        if not planners_names: planners_names = f"{planner1['name']}-{planner2['name']}"
        if not planner_1_name: planner_1_name = planner1['name']
        if not planner_2_name: planner_2_name = planner2['name']

        data.extend([(k, planner1['name'], i) for i in planner1['samples']])
        data.extend([(k, planner2['name'], i) for i in planner2['samples']])

        planner_1_mean.append(planner1['mean'])
        planner_1_std.append(planner1['std'])
        planner_2_mean.append(planner2['mean'])
        planner_2_std.append(planner2['std'])

    df = pd.DataFrame(data, columns=["X", "Planner", "Value"])
    # # Create the plot
    # plt.figure(figsize=(10, 6))

    # # Error bar plot
    # plt.errorbar(k_v_sorted, planner_1_mean, yerr=planner_1_std, fmt='-o', label=planner_1_name, capsize=5)
    # plt.errorbar(k_v_sorted, planner_2_mean, yerr=planner_2_std, fmt='-s', label=planner_2_name, capsize=5)

    # # Labels and title
    # # plt.title("Error Bar Plot of Planner Performance")
    # plt.xlabel("K Values")
    # plt.ylabel("Behaviour Count")
    # plt.legend()
    # plt.grid(True)

    # # Save high-res figure
    # plt.savefig(os.path.join(dumpfig, f"{q}_{planners_names}_error_bar_plot.png"), dpi=300, bbox_inches='tight')

    # ------------
    

    # plt.figure(figsize=(10, 6))
    # sns.violinplot(data=df, x="X", y="Value", hue="Planner", split=True, inner="quartile")
    # # plt.title("Violin Plot of Planner's Behaviour Count at Different K Values")
    # plt.ylabel("Behaviour Count")
    # plt.xlabel("K Values")
    # plt.grid(True)
    # plt.tight_layout()
    # plt.savefig(os.path.join(dumpfig, f"{q}_{planners_names}_violin_plot.png"), dpi=300, bbox_inches='tight')  # High resolution PNG
    # -------------


    # # Plot: KDE for each planner at each X value
    # g = sns.FacetGrid(df, col="X", hue="Planner", sharex=True, sharey=True, col_wrap=2, height=4)
    # g.map(sns.kdeplot, "Value", fill=True, common_norm=False, alpha=0.5)
    # g.add_legend()

    # # Title and layout
    # plt.subplots_adjust(top=0.9)
    # g.fig.suptitle("Density Plot (KDE) of Planner Performance Across X Values")

    # # Save the plot
    # plt.savefig(os.path.join(dumpfig, f"{q}_{planners_names}_density_plot.png"), dpi=300, bbox_inches='tight')

    # --------------------
    # # Plot box plot
    # plt.figure(figsize=(10, 6))
    # sns.boxplot(data=df, x="X", y="Value", hue="Planner")
    # plt.yscale("log")
    # plt.xlabel("K Values")
    # plt.ylabel("Behaviour Count")
    # plt.grid(True)

    # # Save plot in high resolution
    # plt.savefig(os.path.join(dumpfig, f"{q}_{planners_names}_box_plot.png"), dpi=300, bbox_inches='tight')
    # -------------------

    # Convert X to string and sort numerically
    df["X"] = df["X"].astype(str)
    x_order = sorted(df["X"].unique(), key=lambda x: int(x))

    # Create the facet grid with all plots in one row
    g = sns.catplot(
        data=df,
        x="Planner",
        y="Value",
        col="X",
        kind="box",
        col_order=x_order,
        height=4,
        aspect=0.8,
        sharey=False,
        palette="Set2"
    )

    # Remove individual subplot x-labels and add one shared x-label
    for ax in g.axes.flat:
        ax.set_xlabel("")

    # Add global x-axis label (centered below)
    g.set_axis_labels("Planner", "Performance")

    # Adjust layout and add a title
    g.fig.subplots_adjust(top=0.85)
    g.fig.suptitle("Box Plots of Planner Performance by X Value (Sorted & in One Row)")

    plt.savefig(os.path.join(dumpfig, f"{q}_{planners_names}_box_plot.png"), dpi=300, bbox_inches='tight')

    # plt.show()
    pass


    pass


resultsdir = "/Users/mustafafaisal/Downloads/paper-results/classical-score-dump-results"
dumpfigs = "/Users/mustafafaisal/Downloads/paper-results/dump-figs"

os.makedirs(dumpfigs, exist_ok=True)

raw_results = read_results(resultsdir)

# get all q values 
q_values = set(map(lambda x: x[0], raw_results))
k_values = set(map(lambda x: x[1], raw_results))
planners = set(map(lambda x: x[2], raw_results))

for (planner1, planner2) in combinations(planners, 2):
    for q in q_values:
        k_planners_values = {}

        for k in k_values:
            planner1_results = list(filter(lambda x: x[0] == q and x[1] == k and x[2] == planner1, raw_results))
            planner2_results = list(filter(lambda x: x[0] == q and x[1] == k and x[2] == planner2, raw_results))
            common_domains = set.intersection(set(map(lambda x: x[3], planner1_results)),set(map(lambda x: x[3], planner2_results)))

            filtered_planner1_results = sorted(filter(lambda x: x[3] in common_domains, planner1_results), key=lambda x: x[3])
            filtered_planner2_results = sorted(filter(lambda x: x[3] in common_domains, planner2_results), key=lambda x: x[3])
            assert len(filtered_planner1_results) == len(filtered_planner2_results), f"Different number of results for {planner1} and {planner2} for q={q} and k={k}"

            # compute normialised mean and std, but use statistics library

            planner1_mean = sum(map(lambda x: x[4], filtered_planner1_results)) / len(filtered_planner1_results)
            planner2_mean = sum(map(lambda x: x[4], filtered_planner2_results)) / len(filtered_planner2_results)
            planner1_std = (sum(map(lambda x: (x[4] - planner1_mean) ** 2, filtered_planner1_results)) / len(filtered_planner1_results)) ** 0.5
            planner2_std = (sum(map(lambda x: (x[4] - planner2_mean) ** 2, filtered_planner2_results)) / len(filtered_planner2_results)) ** 0.5

            k_planners_values[k] = {
                'planner1': {
                    'name': planner1,
                    'mean': round(planner1_mean,3),
                    'std': round(planner1_std,3),
                    'count': len(filtered_planner1_results),
                    'samples': list(map(lambda x: x[4], filtered_planner1_results))
                },
                'planner2': {
                    'name': planner2,
                    'mean': round(planner2_mean,3),
                    'std': round(planner2_std,3),
                    'count': len(filtered_planner2_results),
                    'samples': list(map(lambda x: x[4], filtered_planner2_results))
                }
            }



        plot_planners(q, k_values, k_planners_values, dumpfigs)
    pass



pass