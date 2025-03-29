import os
import json
import statistics

from scipy import stats
from itertools import combinations 
from collections import defaultdict


def read_results(directory):
    # list files in the directory
    instances = set()
    for file in map(lambda x: os.path.join(directory, x), os.listdir(directory)):
        if not file.endswith('.json'): continue
        with open(file, 'r') as f:
            data = json.load(f)
        if len(data) == 0: continue
        if not 'info' in data: continue
        if data['info']['tag'] == 'symk':
            data['info']['tag'] = 'symk-bspace' # I don't now why this bug happens
        instances.add((data['info']['q'], data['info']['k'], f"{data['info']['domain']}-{data['info']['problem']}", data['info']['tag'], data['diversity-scores']['behaviour-count']))        
    return instances

instances = read_results('/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-classical-behaviour-count-exp/score-dump-results')

q_values = set(map(lambda x: x[0], instances))
k_values = set(map(lambda x: x[1], instances))
planners = set(map(lambda x: x[3], instances))

planners_results_rows = defaultdict(dict)
for q in sorted(q_values):
    planners_results_rows[q] = defaultdict(dict)
    for k in sorted(k_values):
        planners_results_rows[q][k] = defaultdict(dict)
        planners_results = []
        
        for planner in planners:
            # filter instances for this q, k, and planner
            filtered_instances = list(filter(lambda x: x[0] == q and x[1] == k and x[3] == planner, instances))
            if len(filtered_instances) == 0: continue
            # get the domain-problem pairs
            planners_results.append((planner, set(map(lambda x: x[2], filtered_instances))))
            
        for planner1, planner2 in combinations(planners_results, 2):
            if not (('fbi' in planner1[0]) or ('fbi' in planner2[0])): continue
            
            planners_key = f'{planner1[0]}-{planner2[0]}'
            planners_results_rows[q][k][planners_key] = defaultdict(dict)
            
            # get common instances for the planners
            common_instances = set.intersection(planner1[1], planner2[1])
            # filter instances for this q, k, and planner
            filtered_instances_planner_1 = list(filter(lambda x: x[0] == q and x[1] == k and x[3] == planner1[0] and x[2] in common_instances, instances))
            filtered_instances_planner_2 = list(filter(lambda x: x[0] == q and x[1] == k and x[3] == planner2[0] and x[2] in common_instances, instances))

            planner1_samples = list(map(lambda e:e[-1], filtered_instances_planner_1))
            planner2_samples = list(map(lambda e:e[-1], filtered_instances_planner_2))

            assert len(planner1_samples) == len(planner2_samples), f"Samples length mismatch: {len(planner1_samples)} != {len(planner2_samples)}"

            planners_results_rows[q][k][planners_key][f'{planner1[0]}-samples'] = planner1_samples
            planners_results_rows[q][k][planners_key][f'{planner2[0]}-samples'] = planner2_samples
            
            planners_results_rows[q][k][planners_key][f'{planner1[0]}-bc'] = sum(planner1_samples)
            planners_results_rows[q][k][planners_key][f'{planner2[0]}-bc'] = sum(planner2_samples)

            planners_results_rows[q][k][planners_key][f'{planner1[0]}-mean'] = round(statistics.mean(planner1_samples),2)
            planners_results_rows[q][k][planners_key][f'{planner2[0]}-mean'] = round(statistics.mean(planner2_samples),2)

            planners_results_rows[q][k][planners_key][f'{planner1[0]}-std'] = round(statistics.stdev(planner1_samples),2)
            planners_results_rows[q][k][planners_key][f'{planner2[0]}-std'] = round(statistics.stdev(planner2_samples),2)

            planners_results_rows[q][k][planners_key][f'{planner1[0]}-coverage'] = len(list(filter(lambda x: x[0] == q and x[1] == k and x[3] == planner1[0], instances)))
            planners_results_rows[q][k][planners_key][f'{planner2[0]}-coverage'] = len(list(filter(lambda x: x[0] == q and x[1] == k and x[3] == planner2[0], instances)))

            planners_results_rows[q][k][planners_key]['p-value'] = round(stats.ttest_rel(*[planner1_samples, planner2_samples]).pvalue, 3)
            planners_results_rows[q][k][planners_key]['common-instances-count'] = len(common_instances)
            

pass