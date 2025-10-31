import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

planner_name_map = {
    'symk': r'$\mathrm{SymK}$',
    'fi-none-bspace': r'$\mathrm{FI_{bc}}$',
    'fi-bspace': r'$\mathrm{FI_{bc}}$',
    'fi-none-first-k': r'$\mathrm{FI_k}$',
    'fi-first-k': r'$\mathrm{FI_k}$',
    'fi-none-maxsum': r'$\mathrm{FI_{max}}$',
    'fi-maxsum': r'$\mathrm{FI_{max}}$',
    'fbi-seq-fd': r'$\mathrm{FBI_{SMT}}$',
    'fbi-seq-fd-naive': r'$\mathrm{FBI_{SMT}^{naive}}$',

    'fbi-seq-seq-naive': r'$\mathrm{FBI_{SMT}^{naive}}$',
    'fbi-seq-seq': r'$\mathrm{FBI_{SMT}}$',

    'fbi-utility-value-naive': r'$\mathrm{FBI_{SMT}^{naive}}$',
    'fbi-utility-value': r'$\mathrm{FBI_{SMT}}$',

}


color_map = {
    r'$\mathrm{FBI_{SMT}}$': '#1f77b4',  # blue
    r'$\mathrm{FI_{bc}}$': '#ff7f0e',  # orange
    r'$\mathrm{FI_k}$': '#2ca02c',  # green
    r'$\mathrm{FI_{max}}$': '#d62728',  # red,
    r'$\mathrm{SymK}$': '#9467bd',  # purple
    r'$\mathrm{FBI_{SMT}^{naive}}$': '#8c564b'  # brown
}

plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 16,
    'axes.labelsize': 16,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 16,
    'figure.titlesize': 16,
    'mathtext.default': 'regular',
    'font.family': 'serif',
    'mathtext.fontset': 'cm'
})


def read_files(path):
    ret_files = []
    for file in os.listdir(path):
        if not file.endswith('.json'): continue
        with open(os.path.join(path, file), 'r') as f:
            data = json.load(f)
            ret_files.append((file, data))
    return ret_files


def do_violin_plot(result, savetofile, sorted_order):
    # sorted_order = ['FI_bc', 'FI_max', 'FI_k', 'SymK', 'FBI_SMT']
    planners_groups = {}
    for k in sorted(result.keys(), key= lambda v: int(v)):
        values = result[k]
        planners = set(map(lambda k: k.replace('-mean','').replace('-samples',''), filter(lambda k: '-samples' in k, values.keys())))
        planner_behaviour_count = []
        for planner in planners:
            samples = values.get(f'{planner}-samples', [])
            planner_behaviour_count.extend(list((planner_name_map[planner], bc) for bc in samples))

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
        ax.set_title(group_name, fontsize=25)
        ax.set_xlabel('')
        ax.grid(True)
        # Adjust x-axis labels to prevent overlapping
        ax.tick_params(axis='x', labelsize=20)
        plt.setp(ax.get_xticklabels(), ha='center')

    # Styling
    axes[0].set_ylabel("Behaviour Count", fontsize=25)
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

# classical - exp.
__sorted_planners_order = [r'$\mathrm{FI_{bc}}$', r'$\mathrm{FBI_{SMT}^{naive}}$', r'$\mathrm{FBI_{SMT}}$']
q_1_0_files = [
    '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/classical/analysis-classic/3-1.0-5-fbi-seq-fd-fbi-seq-fd-naive-fi-bspace.json',
    '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/classical/analysis-classic/3-1.0-10-fbi-seq-fd-fbi-seq-fd-naive-fi-bspace.json',
    '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/classical/analysis-classic/3-1.0-100-fbi-seq-fd-fbi-seq-fd-naive-fi-bspace.json',
    '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/classical/analysis-classic/3-1.0-1000-fbi-seq-fd-fbi-seq-fd-naive-fi-bspace.json'
]

q_2_0_files = [
    '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/classical/analysis-classic/3-2.0-5-fbi-seq-fd-fbi-seq-fd-naive-fi-bspace.json',
    '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/classical/analysis-classic/3-2.0-10-fbi-seq-fd-fbi-seq-fd-naive-fi-bspace.json',
    '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/classical/analysis-classic/3-2.0-100-fbi-seq-fd-fbi-seq-fd-naive-fi-bspace.json',
    '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/classical/analysis-classic/3-2.0-1000-fbi-seq-fd-fbi-seq-fd-naive-fi-bspace.json'
]

# # numeric - exp.
# __sorted_planners_order = [r'$\mathrm{FBI_{SMT}^{naive}}$', r'$\mathrm{FBI_{SMT}}$']
# q_1_0_files = [
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/numeric/analysis-run/2-1.0-5-fbi-seq-seq-naive-fbi-seq-seq.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/numeric/analysis-run/2-1.0-10-fbi-seq-seq-naive-fbi-seq-seq.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/numeric/analysis-run/2-1.0-100-fbi-seq-seq-naive-fbi-seq-seq.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/numeric/analysis-run/2-1.0-1000-fbi-seq-seq-naive-fbi-seq-seq.json'
# ]

# q_2_0_files = [
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/numeric/analysis-run/2-2.0-5-fbi-seq-seq-naive-fbi-seq-seq.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/numeric/analysis-run/2-2.0-10-fbi-seq-seq-naive-fbi-seq-seq.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/numeric/analysis-run/2-2.0-100-fbi-seq-seq-naive-fbi-seq-seq.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/numeric/analysis-run/2-2.0-1000-fbi-seq-seq-naive-fbi-seq-seq.json'
# ]

# __sorted_planners_order = [r'$\mathrm{SymK}$', r'$\mathrm{FBI_{SMT}^{naive}}$', r'$\mathrm{FBI_{SMT}}$']
# # osp - 0.25 - exp
# q_1_0_files = [
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.25/analysis-run/3-1.0-5-symk-fbi-utility-value-fbi-utility-value-naive.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.25/analysis-run/3-1.0-10-symk-fbi-utility-value-fbi-utility-value-naive.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.25/analysis-run/3-1.0-100-symk-fbi-utility-value-fbi-utility-value-naive.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.25/analysis-run/3-1.0-1000-symk-fbi-utility-value-fbi-utility-value-naive.json'
# ]

# # # osp - 0.5 - exp
# q_1_0_files = [
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.5/analysis-run/3-1.0-5-symk-fbi-utility-value-naive-fbi-utility-value.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.5/analysis-run/3-1.0-10-symk-fbi-utility-value-naive-fbi-utility-value.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.5/analysis-run/3-1.0-100-symk-fbi-utility-value-naive-fbi-utility-value.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.5/analysis-run/3-1.0-1000-symk-fbi-utility-value-naive-fbi-utility-value.json'
# ]

# # # osp - 0.75 - exp
# q_1_0_files = [
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.75/analysis-run/3-1.0-5-fbi-utility-value-naive-fbi-utility-value-symk.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.75/analysis-run/3-1.0-10-fbi-utility-value-naive-fbi-utility-value-symk.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.75/analysis-run/3-1.0-100-fbi-utility-value-naive-fbi-utility-value-symk.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/0.75/analysis-run/3-1.0-1000-fbi-utility-value-naive-fbi-utility-value-symk.json'
# ]

# # # osp - 1.0 - exp
# q_1_0_files = [
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/1.0/analysis-run/3-1.0-5-fbi-utility-value-symk-fbi-utility-value-naive.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/1.0/analysis-run/3-1.0-10-fbi-utility-value-symk-fbi-utility-value-naive.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/1.0/analysis-run/3-1.0-100-fbi-utility-value-symk-fbi-utility-value-naive.json',
#     '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-all-results/paper-results/osp/1.0/analysis-run/3-1.0-1000-fbi-utility-value-symk-fbi-utility-value-naive.json'
# ]

# q_2_0_files = []



for q, files in [(1.0, q_1_0_files), (2.0, q_2_0_files)]:
    results = {}
    for file, k in zip(files, [5, 10, 100, 1000]):
        with open(file, 'r') as f:
            data = json.load(f)
            results[k] = data
    do_violin_plot(results, os.path.join(os.path.dirname(file), f'violin-{q}-{os.path.basename(file).replace(".json", ".pdf")}'), __sorted_planners_order)



# classical_results = read_files('/Users/mustafafaisal/Downloads/Supplementary material-2/classical-results/behaviour-count-results')
# dumpdir = os.path.join(os.path.dirname(__file__), '..', '..', 'sandbox-plots', 'classical')
# os.makedirs(dumpdir, exist_ok=True)
# plot_classical_experiments(classical_results, dumpdir)

