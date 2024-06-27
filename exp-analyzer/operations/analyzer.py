import os
import json

from collections import defaultdict
from itertools import combinations

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
    get_common_instances,
    fitler_domain_results,
    combine_behaviour_count,
    combine_per_planner,
    count_solved_instances,
    stringfiy_behaviour_count,
    getkeyvalue
    # stringfiy_coverage
)



def compare_behaviour_count_coverage(resultsdir, dumpdir):
    
    # read the results files.
    domain_results, planners_list = read_files(resultsdir)
    
    # filter the domain_results based on the common instances solved by all the planners.
    common_instances = get_common_instances(domain_results, planners_list)
    
    common_domain_results = fitler_domain_results(domain_results, common_instances)
    planners_behaviour_count_common_results, common_instances_count = combine_behaviour_count(combine_per_planner(common_domain_results))

    # stringfiy the common instances count and the behaviour count coverage.
    csv_dump = stringfiy_behaviour_count(planners_list, planners_behaviour_count_common_results, common_instances_count)
    dump_list_to_csv(csv_dump, os.path.join(dumpdir, "behaviour-count-common-instances.csv"))

# def compute_coverage(resultsdir, dumpdir):
#     # read the results files.
#     domain_results, planners_list = read_files(resultsdir)
#     # now we need to dump the number of solved instances per planner.
#     planners_behaviour_count_results = count_solved_instances(domain_results)
#     csv_dump = stringfiy_coverage(planners_list, planners_behaviour_count_results)
#     dump_list_to_csv(csv_dump, os.path.join(dumpdir, "coverage.csv"))

def compare_planners_results(resultsdir, dumpdir, planner_name=None):
    # read the results files.
    domain_results, planners_list = read_files(resultsdir, planner_name)

def compute_coverage(domain_results, klist):
    solved_domains = set()
    planner_summary = defaultdict(dict)
    for domainname, domainresults in domain_results.items():
        for problemname, problemresults in domainresults.items():
            for q, qresults in problemresults.items():
                for k, kresults in qresults.items():
                    for tag, tagresults in kresults.items():
                        if not q in planner_summary: planner_summary[q] = defaultdict(dict)
                        if not tag in planner_summary[q]: 
                            planner_summary[q][tag]['coverage'] = {kvalue: [] for kvalue in klist}
                            planner_summary[q][tag]['solved-instaces'] = {kvalue: set() for kvalue in klist}
                        for kvalue in klist:
                            planner_summary[q][tag]['coverage'][kvalue].append(kvalue <= tagresults['number-of-plans'])
                            if kvalue <= tagresults['number-of-plans']:
                                planner_summary[q][tag]['solved-instaces'][kvalue].add(f'{domainname}-{problemname}')

    # now count the number of True per k value.
    for q, qresults in planner_summary.items():
        for tag, tagresults in qresults.items():
            for kvalue in klist:
                planner_summary[q][tag]['coverage'][kvalue] = planner_summary[q][tag]['coverage'][kvalue].count(True)
                planner_summary[q][tag]['solved-instaces'][kvalue] = list(planner_summary[q][tag]['solved-instaces'][kvalue])
    return planner_summary

def dump_coverage_results(klist, planner_coverage, planner_tag, dumpdir):
    # dump the results to two files: 1 for the coverage and the other for the solved instances.
    csv_files_dir = os.path.join(dumpdir, 'csv')
    os.makedirs(csv_files_dir, exist_ok=True)
    json_files_dir = os.path.join(dumpdir, 'json')
    os.makedirs(json_files_dir, exist_ok=True)
    coverage_csv_dump = [f'q,k,tag,coverage']
    for q, qresults in planner_coverage.items():
        for tag, tagresults in qresults.items():
            for kvalue in klist:
                coverage_csv_dump.append(f'{q},{kvalue},{tag},{tagresults["coverage"][kvalue]}')
    # dump the planner_coverage details into json file.
    dumped_json_file = os.path.join(json_files_dir, f'{planner_tag}-coverage-details.json')
    with open(dumped_json_file, "w") as f:
        json.dump(planner_coverage, f, indent=4)
    dump_list_to_csv(coverage_csv_dump, os.path.join(csv_files_dir, f'{tag}-coverage.csv'))
    return dumped_json_file

def extract_common_instances(planner1, planner2, planners_files, klist, dumpdir):
    os.makedirs(dumpdir, exist_ok=True)
    common_instances = defaultdict(dict)
    planners_results = dict()
    q_values = set()
    for p in [planner1, planner2]:
        with open(planners_files[p], 'r') as f:
            if len(planners_results) == 0:
                planners_results = json.load(f)
                q_values.update(list(planners_results.keys()))
            else:
                planner_2_results = json.load(f)
                for q in q_values:
                    planners_results[q].update(planner_2_results[q])
    
    # after gathering the planners results, we need to compute the common instances 
    # for this planner pairs.
    for q, planners in planners_results.items():
        common_instances[q] = defaultdict(list)
        for k in klist:
            p1_solved = set(planners[planner1]['solved-instaces'][str(k)])
            p2_solved = set(planners[planner2]['solved-instaces'][str(k)])
            common_instances[q][k] = list(set.intersection(p1_solved, p2_solved))
    
    # save this to json file and return it.
    dumpfile = os.path.join(dumpdir, f'{planner1}-{planner2}-common-instances.json')
    with open(dumpfile, 'w') as f:
        json.dump(common_instances, f, indent=4)
    return dumpfile

def analyze(args):
    # To have a good results, It will be better to read each planner results on its own
    # then dump files for each planner, which will be used to compute the behaviour coverage based on planners.
    os.makedirs(args.output_dir, exist_ok=True)
    dump_common_instances_dir = os.path.join(args.output_dir, 'common-instances-details')

    klist = [5, 10, 100, 1000]
    planners_list = ['symk', 'fi-none', 'fbi-seq']
    planners_files = {}
    for planner_tag in planners_list:
        print(f'Analyzing planner: {planner_tag}')
        # read only the files with the planner_tag.
        domain_results, _ = read_files(args.planner_results_dir, planner_tag)
        planner_coverage = compute_coverage(domain_results, klist)
        dumped_json_file = dump_coverage_results(klist, planner_coverage, planner_tag, args.output_dir)
        planners_files[planner_tag] = dumped_json_file
    
    common_instaces_list = {}
    for planner1, planner2 in combinations(planners_list, 2):
        print(f'Computing the common instances between {planner1}, {planner2}')
        # shit we need to get the q values also.
        # load the results for those two planners.
        dumpfile = extract_common_instances(planner1, planner2, planners_files, klist, dump_common_instances_dir)
        common_instaces_list[(planner1, planner2)] = dumpfile

    pass
                
                
                
                


    pass

    # now we want to compute the common solved instances between the planners.



    # compare_planners_results(args.planner_results_dir, args.output_dir, 'symk')

    # if args.compute_behaviour_count:
    #     compare_behaviour_count_coverage(args.planner_results_dir, args.output_dir)
    # if args.compute_coverage:
    #     compute_coverage(args.planner_results_dir, args.output_dir)
    return 0

def summarise_error(args):
    errors_log = defaultdict(list)
    for file in os.listdir(args.error_files_dir):
        if file.endswith(".error"):
            # read file
            with open(os.path.join(args.error_files_dir, file), "r") as f:
                error = f.read()
                errors_log[error].append(file) 
            pass
    
    # summarise the errors.
    errors_log_summary = {}
    errors_log_summary["total_errors"] = len(errors_log)
    errors_log_summary['error-count'] = defaultdict(dict)
    for error, files in errors_log.items():
        errors_log_summary['error-count'][error] = len(files)
    
    errors_log_summary['details'] = errors_log
    os.makedirs(args.output_dir, exist_ok=True)
    with open(os.path.join(args.output_dir, "errors_summary.json"), "w") as f:
        json.dump(errors_log_summary, f, indent=4)
