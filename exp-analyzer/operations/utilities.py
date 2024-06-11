import os
import json
from collections import defaultdict

def getkeyvalue(data, target_key):
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for value in data.values():
            result = getkeyvalue(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = getkeyvalue(item, target_key)
            if result is not None:
                return result
    return None

def read_files(exp_dir):
    ret_results = defaultdict(dict)
    planners_tags = set()
    no_coverage_available = set()
    skipping_reasons = set()

    # Get all the files in the directory
    for file in os.listdir(exp_dir):
        if file.endswith(".json"):
            results_file = os.path.join(exp_dir, file)
            with open(results_file, "r") as f:
                data = json.load(f)

                if 'reason' in data:
                    skipping_reasons.add((results_file, data['reason']))
                    continue
                
                # read the planning task.
                domain = getkeyvalue(data, "domain")
                problem = getkeyvalue(data, "problem")                
                if not domain in ret_results: ret_results[domain] = defaultdict(dict)
                if not problem in ret_results[domain]: ret_results[domain][problem] = defaultdict(dict)

                # read the quality bound.
                q = getkeyvalue(data, "q")
                if not q in ret_results[domain][problem]: 
                    q = str(q)
                    ret_results[domain][problem][q] = defaultdict(dict)

                # read the required number of plans.
                k = getkeyvalue(data, "k")
                if not k in ret_results[domain][problem][q]: 
                    k = str(k)
                    ret_results[domain][problem][q][k] = defaultdict(dict)

                # read the planner.
                tag = getkeyvalue(data, "tag")
                if not tag in ret_results[domain][problem]: 
                    ret_results[domain][problem][q][k][tag] = defaultdict(dict)
                    ret_results[domain][problem][q][k][tag]["behaviour-count"] = {}

                # read the sat-time
                ret_results[domain][problem][q][k][tag]["sat-time"] = getkeyvalue(data, "sat-time")

                # get the behaviour count socres.
                try:
                    ret_results[domain][problem][q][k][tag]["behaviour-count"].update(getkeyvalue(data, "behaviour-count")) 
                except:
                    ret_results[domain][problem][q][k][tag]["behaviour-count"].update({k: 0})
                    no_coverage_available.add(results_file)

                # add the planner tag to the list of planners.
                planners_tags.add(tag)

    return ret_results, sorted(planners_tags)

def dump_list_to_csv(csv_dump, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for line in csv_dump:
            f.write(line + "\n")
    return 0


def get_planners_list(domain_results):
    planners_list = set()
    for domainname, domainresults in domain_results.items():
        for problemname, problemresults in domainresults.items():
            for q, qresults in problemresults.items():
                for k, kresults in qresults.items():
                    for tag, tagresults in kresults.items():
                        planners_list.add(tag)
    return sorted(planners_list)

def get_common_instances(domain_results, planners_list):
    common_instances = set()
    for domainname, domainresults in domain_results.items():
        for problemname, problemresults in domainresults.items():
            for q, qresults in problemresults.items():
                for k, kresults in qresults.items():
                    if len(kresults) == len(planners_list):
                        # make sure that all the planners have solved the same instances for the given k.
                        solved_tags = [tagresults['behaviour-count'][k] > 0 for _, tagresults in kresults.items()]
                        if not all(solved_tags): continue
                        common_instances.add((domainname, problemname, q))
    return common_instances

def fitler_domain_results(domain_results, filter_list):
    filtered_results = defaultdict(dict)
    for domainname, domainresults in domain_results.items():
        for problemname, problemresults in domainresults.items():
            for q, qresults in problemresults.items():
                for k, kresults in qresults.items():
                    if not (domainname, problemname, q) in filter_list: continue
                    if not domainname in filtered_results: filtered_results[domainname] = defaultdict(dict)
                    if not problemname in filtered_results[domainname]: filtered_results[domainname][problemname] = defaultdict(dict)
                    if not q in filtered_results[domainname][problemname]: filtered_results[domainname][problemname][q] = defaultdict(dict)
                    for tag, tagresults in kresults.items():
                        filtered_results[domainname][problemname][q][tag] = tagresults
    return filtered_results


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
                    if len(raw) == 0: continue # skip empty results, this is cause due to the creation of raw results.
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
                if not k in planners_behaviour_count[q][planner_tag]: 
                    # this case is for fi since it may failed to generate the specific k value.
                    planners_behaviour_count[q][planner_tag][k] = 0
                csv_dump.append(f'{q}, {k}, {kcount}, {planner_tag}, {planners_behaviour_count[q][planner_tag][k]}')
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
                planners_solved_instances_count[q][tag][k] = [ not k in c or c[k] > 0 for c in tagresults['raw']].count(True)
    return planners_solved_instances_count
