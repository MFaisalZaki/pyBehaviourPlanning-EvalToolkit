import os
import json
from argparse import ArgumentParser


common_msgs_commonkey_map_error = {
    'The seed plan ': 'symk-timeouted',
    'Different elements of a problem can have the same name if the environment flag': 'error_used_name is enabled',
    'unbounded variables': 'unbounded variables',
    'Context mismatch': 'context mismatch',
    'Unsupported expression: ': 'Unsupported expression',
    'UPExpressionDefinitionError': 'UPExpressionDefinitionError',
    "Expected ')', found '('": 'parsing error',
    'In precondition: ': 'precondition error',
    'Initial value not set for fluent:': 'Initial value not set for fluent',
    "'PlanGenerationResult' object is not subscriptable": 'PlanGenerationResult object is not subscriptable',
    'Error from line: 26, col 30 to line: 26, col 46': 'Error from line: 26, col 30 to line: 26, col 46',
    'maximum recursion depth exceeded': 'maximum recursion depth exceeded',
    'Some variables in the effect are unbounded: ': 'Some variables in the effect are unbounded',
    "'block'": 'block',
    '{space_level sold}' : 'space_level sold',
    '{observeddomainuser - ': 'observeddomainuser',
    '{observeddomaincredential - ': 'observeddomaincredential',
    "Expected ':init', found ": 'Expected :init',
    'The upper bound is less than or equal to zero.': 'The upper bound is less than or equal to zero',
    "is not an AND or a FLUENT": 'is not an AND or a FLUENT',
}

common_msgs_commonkey_map_bspace = {
    'Plan 0 has been added to the behaviour space.': 'Plan 0 has been added to the behaviour space',
}




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
    parser.add_argument("--error-dir", dest="error_dir", required=True, help="directory containing error json files")
    parser.add_argument("--bspace-results-dir", dest="bspace_results_dir", required=True, help="directory containing bspace results json files")
    args = parser.parse_args()
    return args

def read_error_files_from_directory(directory):
    read_files_list = []
    for filename in os.listdir(directory):
        if filename.endswith(".error"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                lines = file.readlines()
                read_files_list.append((filepath, lines))
    return read_files_list



def group_by_error(errors_msgs, common_msgs_commonkey_map):
    error_dict = {}

    for msg, commonkey in common_msgs_commonkey_map.items():
        error_dict[commonkey] = [] 
    
    uncategorised_msgs = []

    for filename, lines in errors_msgs:
        for line in lines:
            msg_added = False
            for key in list(common_msgs_commonkey_map.keys()):
                if key in line:
                    common_msg = common_msgs_commonkey_map[key]
                    if not common_msg in error_dict: error_dict[common_msg] = []
                    error_dict[common_msg].append(filename)
                    msg_added = True
            if not msg_added: uncategorised_msgs.append(line)
    # Add a frequency key to the dictionary

    ret_dict = {}
    ret_dict['details'] = error_dict
    ret_dict['summary'] = {}
    for key in error_dict:
        ret_dict['summary'][key] = len(error_dict[key])

    return ret_dict

def read_bspace_logs(directory):
    read_files_list = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                data = json.load(file)
                fbi_logs = getkeyvalue(data, 'fbi-logs')
                bspace_logs = getkeyvalue(data, 'bspace-logs')
                read_files_list.append((filepath, fbi_logs + bspace_logs))
    return read_files_list




if __name__ == '__main__':
    args = construct_parser()
    # First summaries the errors thrown.
    error_msgs   = read_error_files_from_directory(args.error_dir)
    grouped_msgs = group_by_error(error_msgs, common_msgs_commonkey_map_error)
    # Dump the error summary to a file in parent directory of args.error_dir
    with open(os.path.join(os.path.dirname(args.error_dir), 'error_summary.json'), 'w') as file:
        json.dump(grouped_msgs, file, indent=4)

    # Second summaries bspace errors from the result files.
    bspace_msgs = read_bspace_logs(args.bspace_results_dir)
    grouped_msgs = group_by_error(bspace_msgs, common_msgs_commonkey_map_bspace)
    # Dump the bspace summary to a file in parent directory of args.bspace_results_dir
    with open(os.path.join(os.path.dirname(args.bspace_results_dir), 'bspace_summary.json'), 'w') as file:
        json.dump(grouped_msgs, file, indent=4)