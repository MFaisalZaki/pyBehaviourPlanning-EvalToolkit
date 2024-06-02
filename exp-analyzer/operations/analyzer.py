import os

from collections import defaultdict
from collections import Counter



from .utilities import (
    read_files,
    dump_list_to_csv
)

# We need a function to read experiments file and group them by planner, domain, problem
def count_solved_instances(results):
    counter_values = defaultdict(dict)
    for domain, domain_results in results.items():
        for problem, problem_results in domain_results.items():
            for k, k_results in problem_results.items():
                for q, q_results in k_results.items():
                    for tag, tag_results in q_results.items():
                        if not q in counter_values: counter_values[q] = defaultdict(dict)
                        if not k in counter_values[q]: counter_values[q][k] = defaultdict(dict)
                        if not tag_results['solved']: continue
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
    # sort based on the q, k then tag.
    csv_dump = sorted(csv_dump, key=lambda x: (float(x.split(",")[0]), int(x.split(",")[1]), x.split(",")[2]))
    csv_dump = ['q, k, tag, solved_instances'] + csv_dump
    return csv_dump

def analyze_sat_time(results):
    def _remove_entries(dict_sat, _to_remove_keys):
        for domain, problem, q, k in _to_remove_keys:
            if domain in dict_sat and problem in dict_sat[domain] and q in dict_sat[domain][problem] and k in dict_sat[domain][problem][q]:
                del dict_sat[domain][problem][q][k]
            if domain in dict_sat and problem in dict_sat[domain] and q in dict_sat[domain][problem] and len(dict_sat[domain][problem][q]) == 0:
                del dict_sat[domain][problem][q]
            if domain in dict_sat and problem in dict_sat[domain] and len(dict_sat[domain][problem]) == 0:
                del dict_sat[domain][problem]
            if domain in dict_sat and len(dict_sat[domain]) == 0:
                del dict_sat[domain]

    planners_tags = set()
    domain_sat_time_results = defaultdict(dict)
    for domain, domain_results in results.items():
        for problem, problem_results in domain_results.items():
            for k, k_results in problem_results.items():
                for q, q_results in k_results.items():
                    for tag, tag_results in q_results.items():
                        if not domain in domain_sat_time_results: domain_sat_time_results[domain] = defaultdict(dict)
                        if not problem in domain_sat_time_results[domain]: domain_sat_time_results[domain][problem] = defaultdict(dict)
                        if not q in domain_sat_time_results[domain][problem]: domain_sat_time_results[domain][problem][q] = defaultdict(dict)
                        if not k in domain_sat_time_results[domain][problem][q]: domain_sat_time_results[domain][problem][q][k] = defaultdict(dict)
                        if not tag in domain_sat_time_results[domain][problem][q][k]: domain_sat_time_results[domain][problem][q][k][tag] = []
                        # ignore the timeout instances,. timeout is 600.0 seconds, we may want to have this as a parameter.
                        timeout_instance = list(map(lambda x: eval(x.split(',')[1]) == 600.0, tag_results["sat-time"]))
                        if any(timeout_instance) > 0: continue
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
            sat_time_per_domain[domain_problem][q][k][tag] = domain_sat_time_results[domain][problem][q][k][tag]
        pass
    
    
    
    
    pass


def analyze_different_encodings(args):
    # read experiments files.
    planners_results = read_files(args.dump_results_dir)
    # count the number of solved instances for each planner inside this configuration
    solved_instaces_count = count_solved_instances(planners_results)
    # dump the results to a CSV file.
    dump_list_to_csv(solved_instaces_count, os.path.join(args.output_dir, "solved_instances.csv"))
    # analyze the sat-time for each planner per domain.
    sat_time_analysis = analyze_sat_time(planners_results)
    pass





def analyze(args):
    if args.compare_different_encodings_run:
        analyze_different_encodings(args)
    return 0