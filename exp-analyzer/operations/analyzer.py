import os

from collections import defaultdict
from collections import Counter



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

def analyze_sat_time(results):

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

def remove_entries_with_more_than_cost_bound(results, cost_bound):
    _remove_keys = []
    _removed_from_planners = defaultdict(dict)
    for domain, domain_results in results.items():
        for problem, problem_results in domain_results.items():
            for q, q_results in problem_results.items():
                for k, k_results in q_results.items():
                    for tag, tag_results in k_results.items():
                        if not tag in _removed_from_planners: _removed_from_planners[tag] = []
                        if max(tag_results["plan-length-range"]) > cost_bound:
                            _remove_keys.append((domain, problem, q, k))
                            _removed_from_planners[tag].append((domain, problem, q, k))
    # start removing the entries.
    remove_entries(results, _remove_keys)
    # string the removed instances count for each planner.
    header = sorted(list(_removed_from_planners.keys()))
    removed_results = [str(len(_removed_from_planners[p])) for p in header]
    return results, [', '.join(header)] + [', '.join(removed_results)]


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
    sat_time_analysis = analyze_sat_time(planners_results)
    pass





def analyze(args):
    if args.compare_different_encodings_run:
        analyze_different_encodings(args)
    return 0