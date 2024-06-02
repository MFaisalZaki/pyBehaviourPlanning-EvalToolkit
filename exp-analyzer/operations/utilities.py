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

                # read the quality bound.
                q = getkeyvalue(data, "q")
                if not q in ret_results[domain][problem]: ret_results[domain][problem][q] = defaultdict(dict)

                # read the required number of plans.
                k = getkeyvalue(data, "k")
                if not k in ret_results[domain][problem][q]: ret_results[domain][problem][q][k] = defaultdict(dict)

                
                # read the planner.
                tag = getkeyvalue(data, "tag")
                if not tag in ret_results[domain][problem]: ret_results[domain][problem][q][k][tag] = defaultdict(dict)

                # read the sat-time
                ret_results[domain][problem][q][k][tag]["sat-time"] = getkeyvalue(data, "sat-time")

                # check if the planner has solved the planning task.
                plans = getkeyvalue(data, "plans")
                ret_results[domain][problem][q][k][tag]["solved"] = not (plans is None or len(plans) < k)

                # get range of plans length.
                ret_results[domain][problem][q][k][tag]["plan-length-range"] = list(map(lambda x:int(x), getkeyvalue(data, 'makespan-optimal-cost-bound')))

    return ret_results

def dump_list_to_csv(csv_dump, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for line in csv_dump:
            f.write(line + "\n")
    return 0

def remove_entries(dict_sat, _to_remove_keys):
    for domain, problem, q, k in _to_remove_keys:
        if domain in dict_sat and problem in dict_sat[domain] and q in dict_sat[domain][problem] and k in dict_sat[domain][problem][q]:
            del dict_sat[domain][problem][q][k]
        if domain in dict_sat and problem in dict_sat[domain] and q in dict_sat[domain][problem] and len(dict_sat[domain][problem][q]) == 0:
            del dict_sat[domain][problem][q]
        if domain in dict_sat and problem in dict_sat[domain] and len(dict_sat[domain][problem]) == 0:
            del dict_sat[domain][problem]
        if domain in dict_sat and len(dict_sat[domain]) == 0:
            del dict_sat[domain]
    return dict_sat
