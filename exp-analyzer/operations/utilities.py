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

def dump_list_to_csv(csv_dump, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        for line in csv_dump:
            f.write(line + "\n")
    return 0
