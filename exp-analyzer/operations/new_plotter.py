import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

planner_name_map = {
    'symk': 'SymK',
    'fi-none-bspace': 'FI_bc',
    'fi-none-first-k': 'FI_k',
    'fi-none-maxsum': 'FI_max',
    'fbi-seq-fd': 'FBI_SMT',

}


color_map = {
    'FBI_SMT': '#1f77b4',  # blue
    'FI_bc': '#ff7f0e',  # orange
    'FI_k': '#2ca02c',  # green
    'FI_max': '#d62728',  # red,
    'SymK': '#9467bd',  # purple
}

plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 16,
    'axes.labelsize': 16,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 16,
    'figure.titlesize': 16
})


def read_files(path):
    ret_files = []
    for file in os.listdir(path):
        if not file.endswith('.json'): continue
        with open(os.path.join(path, file), 'r') as f:
            data = json.load(f)
            ret_files.append((file, data))
    return ret_files


def do_violin_plot(result, savetofile):
    sorted_order = ['FI_bc', 'FI_max', 'FI_k', 'SymK', 'FBI_SMT']
    planners_groups = {}
    for k in sorted(result.keys(), key= lambda v: int(v)):
        values = result[k]
        planners = set(map(lambda k: k.replace('-mean','').replace('-samples',''), filter(lambda k: '-samples' in k, values.keys())))
        planner_behaviour_count = []
        for planner in planners:
            samples = values.get(f'{planner}-samples', [])
            planner_behaviour_count.extend(list((planner_name_map[planner], bc) for bc in map(int, samples.split(','))))

        planners_groups[f'k={k}'] = planner_behaviour_count
        # data = pd.DataFrame(planner_behaviour_count, columns=['Planner', 'Behaviour Count'])
        # # Create violin plot
        # plt.figure(figsize=(10, 6))
        # sns.violinplot(x='Planner', y='Behaviour Count', data=data, inner="box", cut=0, palette=color_map, order=sorted_order)

        # # Styling
        # # plt.title('Violin Plot of Planner Samples')
        # plt.grid(True)
        # plt.tight_layout()
    fig, axes = plt.subplots(1, 4, figsize=(20, 5), sharey=False)
    # Plot each group in a subplot
    for ax, (group_name, planners) in zip(axes, planners_groups.items()):
        df = pd.DataFrame(planners, columns=['Planner', 'Value'])
        _sorted_order = [p for p in sorted_order if p in set(e[0] for e in planners)]
        sns.violinplot(x='Planner', y='Value', data=df, ax=ax, palette=color_map, order=_sorted_order, cut=0, inner='box')
        ax.set_title(group_name)
        ax.set_xlabel('')
        ax.grid(True)

    # Styling
    axes[0].set_ylabel("Behaviour Count")
    for ax in axes[1:]:
        ax.set_ylabel("")

    plt.tight_layout()
    plt.savefig(savetofile, bbox_inches='tight', dpi=600)
    
    
    pass

def plot_classical_experiments(raw_results, dumpdir):
    # for every entry we have a violin plot for it.
    for filename, entry in raw_results:
        for q, v in entry.items():
            do_violin_plot(v, os.path.join(dumpdir, f'{filename}_{q}.pdf'))

    pass


classical_results = read_files('/Users/mustafafaisal/Downloads/Supplementary material-2/classical-results/behaviour-count-results')
dumpdir = os.path.join(os.path.dirname(__file__), '..', '..', 'sandbox-plots', 'classical')
os.makedirs(dumpdir, exist_ok=True)
plot_classical_experiments(classical_results, dumpdir)

