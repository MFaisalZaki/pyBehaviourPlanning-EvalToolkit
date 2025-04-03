import json


reuslts_file = '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-analysis-results/classical-run-analysis/results.json'
with open(reuslts_file, 'r') as f:
    results = json.load(f)

rows = [] 
planners_list = []
for q, qvalues in results.items():
    for k, kvalues in qvalues.items():
        k_row_values = ['bspace', q, k]
        planners_list = sorted(kvalues.keys())
        for planner in sorted(kvalues.keys()):
            fbi_planner = 'fbi-seq-fd'
            non_fbi_planner = planner.replace('fbi-seq-fd-', '')
            if 'fbi' in non_fbi_planner: non_fbi_planner = planner.replace('-fbi-seq-fd', '')
            values = [str(kvalues[planner]['common-instances-count'])]
            values.append(f"${kvalues[planner][f'{fbi_planner}-mean']} \\pm {kvalues[planner][f'{fbi_planner}-std']}$")
            values.append(f"${kvalues[planner][f'{non_fbi_planner}-mean']} \\pm {kvalues[planner][f'{non_fbi_planner}-std']}$")
            k_row_values += values
            pass
        rows.append(','.join(k_row_values))

table = [','.join(['Beh. Space', 'q', 'k', 'ci', *planners_list])] + rows
table = '\n'.join(table)
print(table)

pass