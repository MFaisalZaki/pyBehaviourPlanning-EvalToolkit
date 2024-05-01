import os
import json
from argparse import ArgumentParser
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

def construct_parser():
    parser = ArgumentParser()
    parser.add_argument("--results-dir", dest="results_dir", required=True, help="Directory containing the results files.")
    args = parser.parse_args()
    return args

def read_bspace_results(directory):
    read_files_list = []
    q_values = defaultdict(dict)
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                data = json.load(file)
                planner = getkeyvalue(data, 'planner')
                plans = getkeyvalue(data, 'plans')
                domain = getkeyvalue(data, 'domain')
                problem = getkeyvalue(data, 'problem')
                q = str(getkeyvalue(data, 'q'))
                results_str = 'f{domain}-{problem}-{q}-{planner}'
                read_files_list.append((results_str, len(plans)))
                k = len(plans)

                if not q in q_values:
                    q_values[q] = defaultdict(dict)
                    q_values[q][5] = 0
                    q_values[q][10] = 0
                    q_values[q][100] = 0
                    q_values[q][1000] = 0
                
                if k >= 5: q_values[q][5] += 1
                if k >= 10: q_values[q][10] += 1
                if k >= 100: q_values[q][100] += 1
                if k >= 1000: q_values[q][1000] += 1

    return read_files_list, q_values




if __name__ == '__main__':
    args = construct_parser()
    
    # Second summaries bspace errors from the result files.
    bspace_csv_format, k_values = read_bspace_results(args.results_dir)
    pass
    # # Dump the bspace summary to a file in parent directory of args.bspace_results_dir
    # with open(os.path.join(os.path.dirname(args.bspace_results_dir), 'bspace_summary.json'), 'w') as file:
    #     json.dump(grouped_msgs, file, indent=4)