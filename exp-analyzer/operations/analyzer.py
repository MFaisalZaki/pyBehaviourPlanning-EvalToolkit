import os
import json

from collections import defaultdict


from .utilities import (
    getkeyvalue
)
# We need a function to read experiments file and group them by planner, domain, problem

def read_files(exp_dir):
    ret_results = defaultdict(dict)
    # Get all the files in the directory
    for file in os.listdir(exp_dir):
        if file.endswith(".json"):
            with open(os.path.join(exp_dir, file), "r") as f:
                data = json.load(f)
                
                # Read the planning task.
                domain = getkeyvalue(data, "domain")
                problem = getkeyvalue(data, "problem")                
                if not domain in ret_results: ret_results[domain] = defaultdict(dict)
                if not problem in ret_results[domain]: ret_results[domain][problem] = defaultdict(dict)

                # read the required number of plans.
                k = getkeyvalue(data, "k")
                if not k in ret_results[domain][problem]: ret_results[domain][problem][k] = defaultdict(dict)

                # read the quality bound.
                q = getkeyvalue(data, "q")
                if not q in ret_results[domain][problem][k]: ret_results[domain][problem][k][q] = defaultdict(dict)
                
                # read the planner.
                tag = getkeyvalue(data, "tag")
                if not tag in ret_results[domain][problem]: ret_results[domain][problem][k][q][tag] = defaultdict(dict)

                # read the sat-time
                ret_results[domain][problem][k][q][tag]["sat-time"] = getkeyvalue(data, "sat-time")

    return ret_results


def count_solved_instances(results):
    counter_values = defaultdict(dict)
    for domain, domain_results in results.items():
        for problem, problem_results in domain_results.items():
            for k, k_results in problem_results.items():
                for q, q_results in k_results.items():
                    for tag, tag_results in q_results.items():
                        if not q in counter_values: counter_values[q] = defaultdict(dict)
                        if not k in counter_values[q]: counter_values[q][k] = defaultdict(dict)
                        if not tag in counter_values[q][k]: counter_values[q][k][tag] = []
                        counter_values[q][k][tag].append(os.path.join(domain, problem))

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
                csv_dump.append(f'{q}, {k}, {tag}, {tag_results}')
    # sort based on the k then tag.
    csv_dump = sorted(csv_dump, key=lambda x: (float(x.split(",")[0]), int(x.split(",")[1]), x.split(",")[2]))
    csv_dump = ['q, k, tag, solved_instances'] + csv_dump
    return csv_dump

def dump_list_to_csv(csv_dump, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for line in csv_dump:
            f.write(line + "\n")
    return 0


def analyze_different_encodings(args):
    # read experiments files.
    planners_results = read_files(args.dump_results_dir)
    # count the number of solved instances for each planner inside this configuration
    solved_instaces_count = count_solved_instances(planners_results)
    # dump the results to a CSV file.
    dump_list_to_csv(solved_instaces_count, os.path.join(args.output_dir, "solved_instances.csv"))
    pass





def analyze(args):
    if args.compare_different_encodings_run:
        analyze_different_encodings(args)
    return 0