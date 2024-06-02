import os
import shutil

from collections import defaultdict
from collections import Counter
from itertools import cycle

# try to install matplotlib
try:
    import matplotlib.pyplot as plt
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt
    
from .utilities import (
    read_files,
    dump_list_to_csv,
    remove_entries
)

# We need a function to read experiments file and group them by planner, domain, problem
def count_solved_instances(results):
    counter_values = defaultdict(dict)
    for domain, domain_results in results.items():
        for problem, problem_results in domain_results.items():
            for q, q_results in problem_results.items():
                for k, k_results in q_results.items():
                    for tag, tag_results in k_results.items():
                        if not q in counter_values: counter_values[q] = defaultdict(dict)
                        if not k in counter_values[q]: counter_values[q][k] = defaultdict(dict)
                        if not tag_results['solved']: continue
                        if not tag in counter_values[q][k]: counter_values[q][k][tag] = []
                        counter_values[q][k][tag].append(os.path.join(domain, problem))

    # Count the common instances.
    common_instances = defaultdict(dict)
    for q, q_results in counter_values.items():
        for k, k_results in q_results.items():
            common_instances[q][k] = len(set.intersection(*map(set, k_results.values())))

    # Now count the number of solved instances for each planner inside this configuration
    for q, q_results in counter_values.items():
        for k, k_results in q_results.items():
            for tag, tag_results in k_results.items():
                counter_values[q][k][tag] = len(tag_results)

    # now we need to have a list for CSV dump.
    csv_dump = []
    for q, q_results in counter_values.items():
        for k, k_results in q_results.items():
            for tag, tag_results in k_results.items():
                csv_dump.append(f'{q}, {k}, {common_instances[q][k]}, {tag}, {tag_results}')
    # sort based on the q, k then tag.
    csv_dump = sorted(csv_dump, key=lambda x: (float(x.split(",")[0]), int(x.split(",")[1]), x.split(",")[3]))
    csv_dump = ['q, k, common instances, tag, solved_instances'] + csv_dump
    return csv_dump

def analyze_sat_time(results, dump_dir):

    planners_tags = set()
    domain_sat_time_results = defaultdict(dict)
    for domain, domain_results in results.items():
        for problem, problem_results in domain_results.items():
            for q, q_results in problem_results.items():
                for k, k_results in q_results.items():
                    for tag, tag_results in k_results.items():
                        if not domain in domain_sat_time_results: domain_sat_time_results[domain] = defaultdict(dict)
                        if not problem in domain_sat_time_results[domain]: domain_sat_time_results[domain][problem] = defaultdict(dict)
                        if not q in domain_sat_time_results[domain][problem]: domain_sat_time_results[domain][problem][q] = defaultdict(dict)
                        if not k in domain_sat_time_results[domain][problem][q]: domain_sat_time_results[domain][problem][q][k] = defaultdict(dict)
                        if not tag in domain_sat_time_results[domain][problem][q][k]: domain_sat_time_results[domain][problem][q][k][tag] = []
                        # ignore the timeout instances,. timeout is 600.0 seconds, we may want to have this as a parameter.
                        timeout_instance = list(map(lambda x: eval(x.split(',')[1]) == 600.0, tag_results["sat-time"]))
                        if any(timeout_instance) > 0: continue
                        index = next((index for index, item in enumerate(tag_results["sat-time"]) if 'False' in item), None)
                        # remove the sat time for the plans and focus on the sat time for the behaviours only.
                        if index is not None: tag_results["sat-time"] = tag_results["sat-time"][:index]
                        domain_sat_time_results[domain][problem][q][k][tag].append(tag_results["sat-time"])
                        planners_tags.add(tag)

    # now select the problem instances that are solved by all the planners.
    solved_instances_by_all_planners = []
    for domain, domain_results in domain_sat_time_results.items():
        for problem, problem_results in domain_results.items():
            for q, q_results in problem_results.items():
                for k, k_results in q_results.items():
                    for tag, tag_results in k_results.items():
                        solved_instances_by_all_planners.append((domain, problem, q, k))
    solved_instances_by_all_planners = list(filter(lambda item: item[1] == len(planners_tags), Counter(solved_instances_by_all_planners).items()))

    # gather the sat time for each planner per domain.
    sat_time_per_domain = defaultdict(dict)
    for (domain, problem, q, k), _ in solved_instances_by_all_planners:
        domain_problem = os.path.join(domain, problem).replace(".pddl", "").replace("/", "-")
        sat_time_per_domain[domain_problem] = defaultdict(dict)
        sat_time_per_domain[domain_problem][q] = defaultdict(dict)
        sat_time_per_domain[domain_problem][q][k] = defaultdict(dict)
        for tag in planners_tags:
            sat_time_per_domain[domain_problem][q][k][tag] = list(map(lambda x: round(float(x.split(',')[1]),3), domain_sat_time_results[domain][problem][q][k][tag].pop()))
    # remove old sat time dump directory.
    dump_dir = os.path.join(dump_dir, "sat-time")
    if os.path.exists(dump_dir): shutil.rmtree(dump_dir)
    # create a dump directory for the sat time analysis.
    os.makedirs(dump_dir, exist_ok=True)

    colors  = ['b', 'r', 'g', 'm', 'c', 'y', 'k']
    markers = ['o', 's', '^', 'd', 'v', '*', 'x']

    # dump the sat time for each planner per domain.
    for domain_problem, domain_problem_results in sat_time_per_domain.items():
        for q, q_results in domain_problem_results.items():
            for k, k_results in q_results.items():

                plt.figure(figsize=(10, 6))
                x_ticks = list(range(1, k+1)) # no of behaviours

                # unifiy the length of the sat time for each planner.
                # duplicate the last sat time for each planner to make them equal.
                planner_index = 0
                for tag, tag_results in k_results.items():
                    if len(tag_results) < k:
                        tag_results += [tag_results[-1]] * (k - len(tag_results))
                    elif len(tag_results) > k:
                        tag_results = tag_results[:k]
                    plt.plot(x_ticks, tag_results, label=tag, color=colors[planner_index], marker=markers[planner_index])
                    planner_index += 1

                plt.xlabel('Behaviours')
                plt.ylabel('SAT Time (s)')
                plt.title(f'{domain_problem} - q={q}, k={k}')
                plt.legend()
                plt.grid()
                plt.tight_layout()
                plt.savefig(os.path.join(dump_dir, f"{domain_problem}-{q}-{k}.png"))
                plt.close()

def remove_entries_with_more_than_cost_bound(results, cost_bound):
    _remove_keys = []
    _removed_from_planners = defaultdict(dict)
    planners_tags = set()
    for domain, domain_results in results.items():
        for problem, problem_results in domain_results.items():
            for q, q_results in problem_results.items():
                for k, k_results in q_results.items():
                    for tag, tag_results in k_results.items():
                        if not q in _removed_from_planners: _removed_from_planners[q] = defaultdict(dict)
                        if not k in _removed_from_planners[q]: _removed_from_planners[q][k] = defaultdict(dict)
                        if not tag in _removed_from_planners[q][k]: _removed_from_planners[q][k][tag] = []
                        if max(tag_results["plan-length-range"]) > cost_bound:
                            _remove_keys.append((domain, problem, q, k))
                            _removed_from_planners[q][k][tag].append((domain, problem, q, k))
                        planners_tags.add(tag)
    # start removing the entries.
    remove_entries(results, _remove_keys)
    removed_entries = [', '.join(['q', 'k'] + sorted(planners_tags))]
    # stringfiy the removed instances count for each planner.
    for q, q_results in _removed_from_planners.items():
        for k, k_results in q_results.items():
            removed_entries += [', '.join([str(q), str(k)] + [str(len(_removed_from_planners[q][k][p])) for p in sorted(planners_tags)]) ]
    return results, removed_entries

def analyze_different_encodings(args):
    # read experiments files.
    planners_results = read_files(args.dump_results_dir)
    # remove any instances where any of the planner generates plans with more that a cost bound of 25.
    planners_results, removed_instances_count = remove_entries_with_more_than_cost_bound(planners_results, 25)
    # count the number of solved instances for each planner inside this configuration
    solved_instaces_count = count_solved_instances(planners_results)
    # append the number of removed instances.
    solved_instaces_count +=  ['------ removed instances count ------'] + removed_instances_count
    # dump the results to a CSV file.
    dump_list_to_csv(solved_instaces_count, os.path.join(args.output_dir, "solved_instances.csv"))
    # analyze the sat-time for each planner per domain.
    sat_time_analysis = analyze_sat_time(planners_results, args.output_dir)





def analyze(args):
    if args.compare_different_encodings_run:
        analyze_different_encodings(args)
    return 0