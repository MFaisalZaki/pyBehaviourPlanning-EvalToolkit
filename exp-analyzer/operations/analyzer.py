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
    remove_entries,
    getkeyvalue,
    get_planners_list,
    get_common_instances,
    fitler_domain_results
)


def combine_per_planner(domain_results):
    planners_results = defaultdict(dict)
    for domainname, domainresults in domain_results.items():
        for problemname, problemresults in domainresults.items():
            for q, qresults in problemresults.items():
                for k, kresults in qresults.items():

                    for tag, tagresults in kresults.items():
                        if not q in planners_results: planners_results[q] = defaultdict(dict)
                        if not tag in planners_results[q]: planners_results[q][tag] = {'raw': [], 'behaviour-count': {}}
                        behaviour_count_values = getkeyvalue(tagresults, "behaviour-count")
                        if behaviour_count_values is None: continue
                        planners_results[q][tag]['raw'].append(behaviour_count_values)            
    return planners_results

def combine_behaviour_count(planners_results):
    planners_behaviour_count = defaultdict(dict)
    common_instances_count = defaultdict(dict)
    for q, qresults in planners_results.items():
        if not q in planners_behaviour_count: planners_behaviour_count[q] = defaultdict(dict)
        if not q in common_instances_count: common_instances_count[q] = defaultdict(dict)
        for tag, tagresults in qresults.items():
            if not tag in planners_behaviour_count[q]: planners_behaviour_count[q][tag] = {}
            k_values = list(tagresults['raw'][0].keys())
            for k in k_values:
                if not k in planners_behaviour_count[q][tag]: planners_behaviour_count[q][tag][k] = 0
                if not k in common_instances_count[q]: common_instances_count[q][k] = 0
                behaviour_count_per_k = []
                for raw in tagresults['raw']:
                    assert k in raw, f"Key {k} not found in {raw}"
                    behaviour_count_per_k.append(raw[k])
                common_instances_count[q][k] = len(behaviour_count_per_k)
                planners_behaviour_count[q][tag][k] = sum(behaviour_count_per_k)
    return planners_behaviour_count, common_instances_count

def stringfiy_behaviour_count(plannerslist, planners_behaviour_count, common_instances_count):
    csv_dump = ['q, k, common instances, tag, behaviour count']
    q_list = sorted(planners_behaviour_count.keys())
    for q, qresults in common_instances_count.items():
        for k, kcount in qresults.items():
            for planner_tag in plannerslist:
                assert planner_tag in planners_behaviour_count[q], f"Planner {planner_tag} not found in {planners_behaviour_count[q]}"
                assert k in planners_behaviour_count[q][planner_tag], f"Key {k} not found in {planners_behaviour_count[q][planner_tag]}"
                csv_dump.append(f'{q}, {k}, {kcount}, {planner_tag}, {planners_behaviour_count[q][planner_tag][k]}')
            # for tag, tagresults in planners_behaviour_count[q].items():
                # csv_dump.append(f'{q}, {k}, {kcount}, {tag}, {tagresults[k]}')
    return csv_dump

def stringfiy_coverage(plannerslist, planners_solved_instances_count):
    csv_dump = ['q, k, tag, coverage']
    # get k values.
    klist = set()
    for q, qresults in planners_solved_instances_count.items():
        for tag, tagresults in qresults.items():
            for k, kcount in tagresults.items():
                klist.add(k)
    klist = sorted(klist, key=int)
    for q, qresults in planners_solved_instances_count.items():
        for k in klist:
            for planner_tag in plannerslist:
                assert planner_tag in qresults, f"Planner {planner_tag} not found in {qresults}"
                assert k in qresults[planner_tag], f"Key {k} not found in {qresults[planner_tag]}"
                csv_dump.append(f'{q}, {k}, {planner_tag}, {qresults[planner_tag][k]}')

    return csv_dump

def count_solved_instances(domain_results):
    planners_results = combine_per_planner(domain_results)
    planners_solved_instances_count = defaultdict(dict)
    for q, qresults in planners_results.items():
        if not q in planners_solved_instances_count: planners_solved_instances_count[q] = defaultdict(dict)
        for tag, tagresults in qresults.items():
            if not tag in planners_solved_instances_count[q]: planners_solved_instances_count[q][tag] = {}
            k_values = list(tagresults['raw'][0].keys())
            for k in k_values:
                planners_solved_instances_count[q][tag][k] = [ c[k] > 0 for c in tagresults['raw']].count(True)
    return planners_solved_instances_count


def compare_behaviour_count_coverage(resultsdir, dumpdir):
    
    # read the results files.
    domain_results = read_files(resultsdir)
    
    # get the list of planners.
    planners_list = get_planners_list(domain_results)
    
    # combine the results per planner.
    planners_results = combine_per_planner(domain_results)
    
    # filter the domain_results based on the common instances solved by all the planners.
    common_instances = get_common_instances(domain_results, planners_list)
    
    common_domain_results = fitler_domain_results(domain_results, common_instances)
    planners_behaviour_count_common_results, common_instances_count = combine_behaviour_count(combine_per_planner(common_domain_results))

    # stringfiy the common instances count and the behaviour count coverage.
    csv_dump = stringfiy_behaviour_count(planners_list, planners_behaviour_count_common_results, common_instances_count)
    dump_list_to_csv(csv_dump, os.path.join(dumpdir, "behaviour-count-common-instances.csv"))
    
    # now we need to dump the number of solved instances per planner.
    planners_behaviour_count_results = count_solved_instances(domain_results)
    csv_dump = stringfiy_coverage(planners_list, planners_behaviour_count_results)
    dump_list_to_csv(csv_dump, os.path.join(dumpdir, "coverage.csv"))



def analyze(args):
    if args.compare_behaviour_count_coverage:
        compare_behaviour_count_coverage(args.planner_results_dir, args.output_dir)
    return 0