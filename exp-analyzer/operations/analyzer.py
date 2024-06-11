import os
import json

from collections import defaultdict

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
    stringfiy_coverage
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

def compute_coverage(resultsdir, dumpdir):
    # read the results files.
    domain_results, planners_list = read_files(resultsdir)
    # now we need to dump the number of solved instances per planner.
    planners_behaviour_count_results = count_solved_instances(domain_results)
    csv_dump = stringfiy_coverage(planners_list, planners_behaviour_count_results)
    dump_list_to_csv(csv_dump, os.path.join(dumpdir, "coverage.csv"))

def analyze(args):
    if args.compute_behaviour_count:
        compare_behaviour_count_coverage(args.planner_results_dir, args.output_dir)
    if args.compute_coverage:
        compute_coverage(args.planner_results_dir, args.output_dir)
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
