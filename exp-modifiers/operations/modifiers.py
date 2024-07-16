import os 
import json
from copy import deepcopy
    
from .utilities import (
    getkeyvalue,
    setkeyvalue
)

def replace(args):
    for file in os.listdir(args.dir):
        if file.endswith(".json"):        
            results_file = os.path.join(args.dir, file)
            
            with open(results_file, "r") as f:
                data = json.load(f)
            
            domainfile  = getkeyvalue(data, "domainfile")
            problemfile = getkeyvalue(data, "problemfile")

            assert domainfile is not None and problemfile is not None, f"Domain or problem file not found in {results_file}."
            
            old_base_project_name = os.path.dirname(args.sandbox_dir_tag)
            new_base_project_name = os.path.dirname(args.sandbox_dir_value)

            domainfile  = domainfile.replace(old_base_project_name,  new_base_project_name)
            problemfile = problemfile.replace(old_base_project_name, new_base_project_name)

            dims = getkeyvalue(data, "dims")
            new_dims = []
            for idx, (dimname, additional_info) in enumerate(dims):
                if "Resource" in dimname:
                    additional_info = additional_info.replace(args.sandbox_dir_tag, args.sandbox_dir_value)
                new_dims.append([dimname, additional_info])

            assert setkeyvalue(data, "domainfile", domainfile), f"Domain file not updated in {results_file}."
            assert setkeyvalue(data, "problemfile", problemfile), f"Problem file not updated in {results_file}."
            assert setkeyvalue(data, "dims", new_dims), f"Dims not updated in {results_file}."

            with open(results_file, "w") as f:
                json.dump(data, f, indent=4)


def update_symk_oversubscription_dims(args):
    
    os.makedirs(args.dump_dir, exist_ok=True)
    
    for file in os.listdir(args.dir):
        if file.endswith(".json"):
            if not 'symk' in file: continue
            results_file = os.path.join(args.dir, file)
            with open(results_file, "r") as f:
                data = json.load(f)
            
            plans = getkeyvalue(data, 'plans')
            tag = getkeyvalue(data, 'tag')
            if len(plans) == 0: continue

            assert setkeyvalue(data, 'dims', []), f"Dims not found in {results_file}."

            # now we need to have two copies of behaviour space.
            # update the tag.
            space_versions = [('util-set',   [["MakespanOptimalCost", {}], ["UtilitySet",   {'cost-bound-factor': args.cost_bound}]]),\
                              ('util-value', [["MakespanOptimalCost", {}], ["UtilityValue", {'cost-bound-factor': args.cost_bound}]])]
            for t, dim in space_versions:
                data_copy = deepcopy(data)
                filename = os.path.basename(results_file)
                filename = filename.replace(f'{tag}', f"{tag}-{t}")
                setkeyvalue(data_copy, 'tag', f"{tag}-{t}")
                setkeyvalue(data_copy, 'dims', dim)
                with open(os.path.join(args.dump_dir, filename), "w") as f:
                    json.dump(data_copy, f, indent=4)

def add_oversubscription_flag(args):
    for file in os.listdir(args.dir):
        if file.endswith(".json"):        
            results_file = os.path.join(args.dir, file)

            with open(results_file, "r") as f:
                data = json.load(f)

            data['is-oversubscription'] = True

            data['info']['tag'] = f"{data['info']['tag']}-seq"

            filename = os.path.basename(results_file).replace('.json', '-seq.json')
            filepath = os.path.join(os.path.dirname(results_file), filename)

            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)