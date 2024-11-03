import os
import json

from collections import defaultdict
from itertools import combinations
from scipy import stats
from statistics import mean

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
    getkeyvalue,
    read_score_files,
    extract_behaviour_count
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
    os.makedirs(dump_common_instances_dir, exist_ok=True)

    dump_behaviour_count_results = os.path.join(args.output_dir, 'behaviour-count-results')
    os.makedirs(dump_behaviour_count_results, exist_ok=True)

    klist = [5, 10, 100, 1000]
    q_values = set()
    planners_list = ['symk', 'fi-none-bspace', 'fi-none-maxsum', 'fi-none-first-k', 'fbi-seq']
    planners_list = ['symk-util-value', 'symk-util-set', 'fbi-utility-value', 'fbi-utility-set']
    planners_list = ['symk', 'fbi-utility-value-seq']
    planners_list = ['fbi-ppltl', 'symk', 'fi-none-bspace', 'fi-none-maxsum', 'fi-none-first-k']
    # planners_list = ['fi-none-bspace', 'fi-none-maxsum', 'fi-none-first-k']
    # planners_list = ['fi-none-bspace', 'fi-none-maxsum']
    planners_results = defaultdict(dict)
    for planner_tag in planners_list:
        if not planner_tag in planners_results: planners_results[planner_tag] = defaultdict(dict)
        for k in klist:
            print(f'Analyzing planner: {planner_tag} - k:{k}')
            _k_planner_results = read_score_files(args.planner_results_dir, planner_tag, k)
            # populate the results.
            for q, qvalues in _k_planner_results.items():
                q_values.add(q)
                if not q in planners_results[planner_tag]: 
                    planners_results[planner_tag][q] = defaultdict(dict)
                    planners_results[planner_tag][q][k] = defaultdict(dict)
                planners_results[planner_tag][q][k].update(qvalues[k])
    
    planners_files = {}
    for planner1, planner2 in combinations(list(planners_results.keys()), 2):
        # Here we need to get the common instances for this pair.
        common_instances = defaultdict(dict)
        for q in q_values:
            common_instances[q] = defaultdict(dict)
            for k in klist:
                common_instances[q][k] = list(set.intersection(planners_results[planner1][q][k]['solved-domains'], planners_results[planner2][q][k]['solved-domains']))

        # dump this to file.
        dump_json = os.path.join(dump_common_instances_dir, f'{planner1}-{planner2}-common-instances.json')
        planners_files[(planner1, planner2)] = dump_json
        with open(dump_json, 'w') as f:
            json.dump({'common-instances':common_instances}, f, indent=4)

    for (planner1, planner2), common_instances_file in planners_files.items():
        # get the common instances values.
        with open(common_instances_file, 'r') as f:
            common_instances = json.load(f)['common-instances']
        
        planners_bc_results = {}
        # now we need to extract the behaviour count for those instances.
        for q, k_instances in common_instances.items():
            planners_bc_results[q] = defaultdict(dict)
            for k, ci_domains_list in k_instances.items():
                planners_bc_results[q][k] = defaultdict(dict)
                samples_values = []
                _debug_domain = []
                for planner in [planner1, planner2]:
                    print(f'Extracting behaviour count for {planner} - q:{q} - k:{k}')
                    common_bc_values = extract_behaviour_count(args.planner_results_dir, ci_domains_list, planner, k, q)
                    coverage = extract_behaviour_count(args.planner_results_dir, [], planner, k, q)

                    _debug_domain.append(list(map(lambda v:v[0], sorted(common_bc_values[q][str(k)]['samples'], key=lambda x: x[0]))))

                    samples_values.append(list(map(lambda v:v[1], sorted(common_bc_values[q][str(k)]['samples'], key=lambda x: x[0]))))
                    planners_bc_results[q][str(k)][f'{planner}-bc'] = common_bc_values[q][str(k)]['bc']
                    planners_bc_results[q][str(k)][f'{planner}-coverage'] = len(coverage[q][str(k)]['samples'])
                    planners_bc_results[q][str(k)][f'{planner}-samples'] = ','.join(map(str, samples_values[-1]))
                    planners_bc_results[q][str(k)][f'{planner}-samples-mean'] = mean(samples_values[-1])
                assert len(samples_values[0]) == len(samples_values[1]), f'Error: {planner1} and {planner2} have different number of samples'
                assert len(samples_values[0]) == len(ci_domains_list), f'Error: {planner1} and {planner2} have different number of samples'

                planners_bc_results[q][str(k)]['p-value'] = stats.ttest_rel(*samples_values).pvalue
                planners_bc_results[q][str(k)]['ci-#'] = len(ci_domains_list)
        
        # dump this to file.
        dump_json = os.path.join(dump_behaviour_count_results, f'{planner1}-{planner2}-common-instances-behaviour-count.json')
        with open(dump_json, 'w') as f:
            json.dump(planners_bc_results, f, indent=4)

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

def pprint_stats_file(args):
    import pstats
    from pstats import SortKey
    statsfile = pstats.Stats(args.stats_file)
    statsfile.sort_stats(SortKey.CUMULATIVE).print_stats(100)


def analyze_single(args):
    # To have a good results, It will be better to read each planner results on its own
    # then dump files for each planner, which will be used to compute the behaviour coverage based on planners.
    os.makedirs(args.output_dir, exist_ok=True)
    dump_common_instances_dir = os.path.join(args.output_dir, 'common-instances-details')
    os.makedirs(dump_common_instances_dir, exist_ok=True)

    dump_behaviour_count_results = os.path.join(args.output_dir, 'behaviour-count-results')
    os.makedirs(dump_behaviour_count_results, exist_ok=True)

    klist = [5, 10, 100, 1000]
    q_values = set()
    planners_results = defaultdict(dict)
    planner_tag = 'fbi-seq-seq'
    planner = 'fbi'
    planner_bc_results = {}
    if not planner_tag in planners_results: planners_results[planner_tag] = defaultdict(dict)
    for k in klist:
        print(f'Analyzing planner: {planner_tag} - k:{k}')
        _k_planner_results = read_score_files(args.planner_results_dir, planner_tag, k)
        # populate the results.
        for q, qvalues in _k_planner_results.items():
            q_values.add(q)
    
    for q in q_values:
        planner_bc_results[q] = defaultdict(dict)
        for k in klist:
            planner_bc_results[q][k] = defaultdict(dict)  
            coverage = extract_behaviour_count(args.planner_results_dir, [], planner_tag, k, str(q))
            planner_bc_results[q][k][f'{planner}-bc'] = coverage[str(q)][k]['bc']
            planner_bc_results[q][k][f'{planner}-coverage'] = len(coverage[str(q)][k]['samples'])
    
    dump_json = os.path.join(dump_behaviour_count_results, f'{planner}-behaviour-count.json')
    with open(dump_json, 'w') as f:
        json.dump(planner_bc_results, f, indent=4)
    pass