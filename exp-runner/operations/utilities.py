from collections import defaultdict
from collections import OrderedDict
from copy import deepcopy
import os
import json
import importlib.util

from unified_planning.io import PDDLWriter
from unified_planning.model.metrics import Oversubscription
from unified_planning.shortcuts import CompilationKind
from unified_planning.shortcuts import OperatorKind

# from behaviour_planning.over_domain_models.smt.shortcuts import *
# from behaviour_planning.over_domain_models.ppltl.shortcuts import *

import unified_planning as up

def replace_hyphens_in_pddl(file_path, dump_dir):
    # Step 2: Open the input file in read mode
    with open(file_path, 'r') as file:
        # Step 3: Read the content of the file
        content = file.read()
    
    # Step 4: Replace all instances of '-' with '_'
    modified_content = content.replace('-', '_')
    
    # Step 5: Create a new file path by appending '_modified' to the original file name
    base_name = os.path.basename(file_path)
    base, ext = os.path.splitext(base_name)
    new_file_name = f"{base}_modified{ext}"
    new_file_path = os.path.join(dump_dir, new_file_name)
    
    # Step 6: Write the modified content to the new file
    with open(new_file_path, 'w') as new_file:
        new_file.write(modified_content)
    
    # Step 7: Return the path of the new file
    return new_file_path

def parse_experiment_details(expdetailsdir:str):
    """
    Parse the experiment details json file.
    """
    expdetails = defaultdict(dict)
    expdetailsjson = os.path.join(expdetailsdir, "exp-details.json")
    # First read the experiment details file.
    assert os.path.exists(expdetailsjson), f"Experiment details file not found: {expdetailsjson}"
    with open(expdetailsjson, "r") as f:
        expdetails['exp-details'] = json.load(f)
    # Update the resource file path.
    expdetails['exp-details']['resources-file-dir'] = expdetails['exp-details']['resources-file-dir'].replace('${currentdir}', os.path.dirname(expdetailsjson))
    # Now read the planners configurations from the planners dir under the expdetailsdir.
    plannersdir = os.path.join(expdetailsdir, "planners")
    assert os.path.exists(plannersdir), f"Planners directory not found: {plannersdir}"
    for planner in os.listdir(plannersdir):
        plannerjson = os.path.join(plannersdir, planner)
        assert os.path.exists(plannerjson), f"Planner json file not found: {plannerjson}"
        expdetails['planners'][planner.replace('.json', '')] = plannerjson
    # convert the skip configurations into a set of tuples.
    expdetails['exp-details']['skip-cfgs'] = set([tuple(cfg) for cfg in expdetails['exp-details']['skip-cfgs']])
    expdetails['exp-details']['selected-planning-instances'] = set(expdetails['exp-details']['selected-planning-instances'])
    return expdetails

def parse_planning_tasks(planningtasksdir:str, resourcesfiledir:str, resourcesdumpdir:str, selected_instances:set):
    # First collect the resoruces information requried.
    resources = _get_resources_details(resourcesfiledir)

    # First collect all the planning tasks from the planning tasks directory.
    planning_domains = _get_planning_domains(planningtasksdir)

    planning_problems = []
    covered_domains = set()

    for domain in planning_domains:
        for domainsroot, _dir, _files in os.walk(domain):
            domainapi = os.path.join(domainsroot, 'api.py')
            _domainbasename = os.path.basename(domainsroot)
            # This is not a valid domain directory.
            if not os.path.exists(domainapi): continue
            # Ignore already processed domains.
            if _domainbasename in covered_domains: continue
            # Process only strips domains.
            if 'adl' in _domainbasename: continue
            _modulename = f'{os.path.basename(domainsroot)}_module'
            module_spec = importlib.util.spec_from_file_location(_modulename, domainapi)
            domain_module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(domain_module)
            domainsproblems = deepcopy(domain_module.domains)
            _domainname = domainsproblems[0]['name']
            _ipc_year   = domainsproblems[0]['ipc']
            domainsproblems[0]['problems'].sort(key=lambda x:x[1])
            for no, problem in enumerate(domainsproblems[0]['problems']):
                _instanceno = no+1
                planning_problem                = defaultdict(dict)
                planning_problem['domainname']  = _domainname
                planning_problem['instanceno']  = _instanceno
                planning_problem['ipc_year']    = _ipc_year
                planning_problem['domainfile']  = os.path.join(os.path.dirname(domainsroot), problem[0])
                planning_problem['problemfile'] = os.path.join(os.path.dirname(domainsroot), problem[1])

                # If selected instances are not empty, then filter the instances.
                if len(selected_instances) > 0 and f"({str(_ipc_year)}, {_domainname}, {_instanceno})" not in selected_instances: 
                    continue

                # check if the domain and problem instance has resources.
                resourcesfile = None
                if _ipc_year in resources and _domainname in resources[_ipc_year]:
                    if str(_instanceno) in resources[_ipc_year][_domainname]:
                        # maybe I'll consider this later.
                        # dump the resources to a file. 
                        resourcesfile = os.path.join(resourcesdumpdir, f'{_domainname}_{_instanceno}_resources.txt')
                        with open(resourcesfile, 'w') as f:
                            f.write(resources[_ipc_year][_domainname][str(_instanceno)])
                        planning_problem['resources'] = resourcesfile
                
                if not resourcesfile:
                    planning_problem['resources'] = resourcesfile
                
                # Ignore if the domain or problem file does not exist.
                if not (os.path.exists(planning_problem['domainfile']) and os.path.exists(planning_problem['problemfile'])): 
                    continue
                planning_problems.append(planning_problem)
                covered_domains.add(os.path.basename(domainsroot))
    return planning_problems

def _get_planning_domains(directory_path):
    planning_domains = []
    for root, dirs, files in os.walk(directory_path):
        for dir_name in dirs:
            if not os.path.exists(os.path.join(root, dir_name, 'api.py')): continue
            planning_domains.append(os.path.join(root, dir_name))
    return planning_domains

def _get_resources_details(resourcesfiledir:str):
    all_resources = defaultdict(dict)
    for root, dirs, files in os.walk(resourcesfiledir):
        for dir_name in dirs:
            domainpath = os.path.join(root, dir_name)
            for resoruce_file in os.listdir(domainpath):
                # load json file and store the data.
                jsonfile = os.path.join(domainpath, resoruce_file)
                with open(jsonfile, 'r') as f:
                    domain_resources = json.load(f)
                year = getkeyvalue(domain_resources, 'year')
                domain = getkeyvalue(domain_resources, 'domain')
                if not year in all_resources: all_resources[year] = defaultdict(dict)
                if not domain in all_resources[year]: all_resources[year][domain] = defaultdict(dict)
                all_resources[year][domain] = domain_resources['instances']
    return all_resources

def construct_solve_cmd(experiment_file):
    main_entry = os.path.join(os.path.dirname(__file__), '..', 'main.py')
    cmd  = f"python3 {main_entry} "
    cmd += "solve "
    cmd += f"--experiment-file {experiment_file}"
    return cmd

def construct_score_cmd(k, experiment_file):
    main_entry = os.path.join(os.path.dirname(__file__), '..', 'main.py')
    cmd  = f"python3 {main_entry} "
    cmd += "score "
    cmd += f"--k {k} "
    cmd += f"--experiment-file {experiment_file}"
    return cmd

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

def updatekeyvalue(data, target_key, newvalue):
    if isinstance(data, dict):
        if target_key in data:
            data[target_key] = newvalue
            return True
        for value in data.values():
            result = updatekeyvalue(value, target_key, newvalue)
    elif isinstance(data, list):
        for item in data:
            result = updatekeyvalue(item, target_key, newvalue)
    return False

def warpCommand(cmd, timelimt, memorylimit, slurmdumpdir, parition):
    return f"""#!/bin/bash
#SBATCH --job-name=task-%x-%j
#SBATCH --partition={parition}
#SBATCH -e {slurmdumpdir}/task-%x-%j.error
#SBATCH -o {slurmdumpdir}/task-%x-%j.output
#SBATCH --cpus-per-task=1
#SBATCH --mem={memorylimit}
#SBATCH --time={timelimt}

{cmd}
"""

def experiment_reader(expfile):
    with open(expfile, 'r') as f:
        expdetails = json.load(f)
    return expdetails

def read_planner_cfg(expfile):
    with open(expfile, 'r') as f:
        expdetails = json.load(f)
    planner_cfgfile = getkeyvalue(expdetails, 'planner-cfg')
    assert planner_cfgfile is not None, "Planner configuration is not provided."
    with open(planner_cfgfile, 'r') as f:
        planner_cfg = json.load(f)
    planner_params = getkeyvalue(planner_cfg, 'planner-parameters')
    assert planner_params is not None, "Planner parameters are not provided."
    return planner_params

def generate_summary_file(task, expdetails, name, planner_params, planlist, logmsgs):
    
    planlist_size = len(planlist)
    planlist = list(OrderedDict.fromkeys(planlist)) # remove duplicates.
    domain  = getkeyvalue(expdetails, 'domainfile')
    problem = getkeyvalue(expdetails, 'problemfile')
    
    results = defaultdict(dict)
    results['info'] = defaultdict(dict)
    results['info']['planner'] = name
    results['info']['tag'] = getkeyvalue(expdetails, 'tag')
    results['info']['planner-params'] = planner_params
    results['info']['task'] = {
        'domain': f'{os.path.basename(os.path.dirname(domain))}/{os.path.basename(domain)}', 
        'problem': os.path.basename(problem),
        'domainfile': domain,
        'problemfile': problem,
        'k': getkeyvalue(expdetails, 'k'),
        'q': getkeyvalue(expdetails, 'q'),
        'duplicate-plans-found': not (len(planlist) == planlist_size)
    }
    results['plans'] = []

    results['plans'] = list(map(lambda p: p if isinstance(p, str) else f'{PDDLWriter(task).get_plan(p)}; {len(p.actions)} cost (unit)', planlist))
    
    # Copy the dimensions.
    results['dims'] = getkeyvalue(expdetails, 'dims')
    updatekeyvalue(results, 'compliation-list', [])

    # say whether this task is oversubscription or not.
    results['is-oversubscription'] = getkeyvalue(expdetails, 'is-oversubscription-planning')

    results['logmsgs'] = logmsgs
    return results

def update_fbi_parameters(planner_params, expdetails):
    from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.base import DimensionConstructorSMT
    from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.goal_predicate_ordering import GoalPredicatesOrderingSMT
    from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.cost_bound_dims import CostBoundSMT
    from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.cost_bound_makespan_optimal import MakespanOptimalCostSMT
    from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.resource_count import ResourceCountSMT
    from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.functions import FunctionsSMT
    from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.utility_value import UtilityValueSMT
    from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.utility_set import UtilitySetSMT

    updated_parameters = deepcopy(planner_params)
    # Check if we have a resource dimension.
    updated_dims = []
    q_value = getkeyvalue(expdetails, 'q')
    is_oversubsscription = getkeyvalue(expdetails, 'is-oversubscription-planning')
    for idx, (dimname, details) in enumerate(getkeyvalue(planner_params, 'dims')):
        updated_dim_details = None
        if any(x in dimname for x in ['Resource', 'Functions']):
            resourcesfile = getkeyvalue(expdetails, 'resources')
            if resourcesfile is not None:
                updated_dim_details = [dimname, resourcesfile]
        # elif any(x in dimname for x in ['UtilitySet', 'UtilityValue']):
        #     cost_bound_additional_information = deepcopy(details)
        #     cost_bound_additional_information.update({'cost-bound-factor': getkeyvalue(expdetails, 'cost-bound-factor')})
        #     updated_dim_details = [dimname, cost_bound_additional_information]
        else:
            updated_dim_details = [dimname, details]

        if updated_dim_details:
            updated_dims.append([eval(updated_dim_details[0]), updated_dim_details[1]])
    
    updated_compilation_list = []
    for idx, (compilationname, kind) in enumerate(getkeyvalue(planner_params, 'compliation-list')):
        try:
            namev = eval(compilationname)
        except:
            namev = compilationname
        kindv = eval(f'CompilationKind.{kind}')
        updated_compilation_list.append([namev, kindv])
    
    updatekeyvalue(updated_parameters, 'dims', updated_dims)
    updatekeyvalue(updated_parameters, 'compliation-list', updated_compilation_list)
    updated_parameters['base-planner-cfg']['k'] = getkeyvalue(expdetails, 'k')
    updated_parameters['bspace-cfg']['quality-bound-factor'] = q_value
    return updated_parameters



def generate_summary_file_ppltl(task, expdetails, name, planner_params, planlist, logmsgs):
    
    planlist_size = len(planlist)
    planlist = list(OrderedDict.fromkeys(planlist)) # remove duplicates.
    domain  = getkeyvalue(expdetails, 'domainfile')
    problem = getkeyvalue(expdetails, 'problemfile')
    
    results = defaultdict(dict)
    results['info'] = defaultdict(dict)
    results['info']['planner'] = name
    results['info']['tag'] = getkeyvalue(expdetails, 'tag')
    results['info']['planner-params'] = planner_params
    results['info']['task'] = {
        'domain': f'{os.path.basename(os.path.dirname(domain))}/{os.path.basename(domain)}', 
        'problem': os.path.basename(problem),
        'domainfile': domain,
        'problemfile': problem,
        'k': getkeyvalue(expdetails, 'k'),
        'q': getkeyvalue(expdetails, 'q'),
        'duplicate-plans-found': not (len(planlist) == planlist_size)
    }
    results['plans'] = []

    results['plans'] = list(map(lambda p: '\n'.join(map(str, p[0].actions)) + f'\n;{len(p[0].actions)} (unit cost)\n' + f';;->{p[1]}', planlist))
    
    # Copy the dimensions.
    results['dims'] = getkeyvalue(expdetails, 'dims')
    updatekeyvalue(results, 'compliation-list', [])
    # say whether this task is oversubscription or not.
    results['is-oversubscription'] = getkeyvalue(expdetails, 'is-oversubscription-planning')
    results['logmsgs'] = logmsgs
    return results


def update_fbippltl_parameters(planner_params, expdetails):
    from behaviour_planning.over_domain_models.ppltl.bss.behaviour_features_library.goal_predicate_ordering import GoalPredicatesOrderingPPLTL
    updated_parameters = deepcopy(planner_params)
    # Check if we have a resource dimension.
    updated_dims = []
    q_value = getkeyvalue(expdetails, 'q')
    k_value = getkeyvalue(expdetails, 'k')
    tmpdir = getkeyvalue(expdetails, 'tmp-dir')
    for idx, (dimname, details) in enumerate(getkeyvalue(planner_params, 'dims')):
        updated_dim_details = None
        if any(x in dimname for x in ['Resource', 'Functions']):
            resourcesfile = getkeyvalue(expdetails, 'resources')
            if resourcesfile is not None:
                updated_dim_details = [dimname, resourcesfile]
        else:
            updated_dim_details = [dimname, details]
        if updated_dim_details:
            updated_dims.append([eval(updated_dim_details[0]), updated_dim_details[1]])
    
    updated_compilation_list = []
    for idx, (compilationname, kind) in enumerate(getkeyvalue(planner_params, 'compliation-list')):
        try:
            namev = eval(compilationname)
        except:
            namev = compilationname
        kindv = eval(f'CompilationKind.{kind}')
        updated_compilation_list.append([namev, kindv])
    
    updatekeyvalue(updated_parameters, 'dims', updated_dims)
    updatekeyvalue(updated_parameters, 'compliation-list', updated_compilation_list)
    updated_parameters['base-planner-cfg'] = {}
    updated_parameters['base-planner-cfg']['k'] = k_value
    updated_parameters['bspace-cfg']['quality-bound-factor'] = q_value
    updated_parameters['bspace-cfg']['tmpdir'] = tmpdir
    # Update the tmpdir

    return updated_parameters




def construct_behaviour_space(planner, dims):

    if planner in ['ForbidBehaviourIterativePPLTL', 'fbi-ppltl']:
        from behaviour_planning.over_domain_models.ppltl.bss.behaviour_features_library.base import DimensionConstructorPPLTL
        from behaviour_planning.over_domain_models.ppltl.bss.behaviour_features_library.goal_predicate_ordering import GoalPredicatesOrderingPPLTL
    else:
        from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.base import DimensionConstructorSMT
        from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.goal_predicate_ordering import GoalPredicatesOrderingSMT
        from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.cost_bound_dims import CostBoundSMT
        from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.cost_bound_makespan_optimal import MakespanOptimalCostSMT
        from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.resource_count import ResourceCountSMT
        from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.functions import FunctionsSMT
        from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.utility_value import UtilityValueSMT
        from behaviour_planning.over_domain_models.smt.bss.behaviour_features_library.utility_set import UtilitySetSMT

    updated_dims = []
    for idx, (dimname, details) in enumerate(dims):
        if 'Resource' in dimname:
            resourcesfile = details
            assert os.path.exists(resourcesfile), f"Resource file does not exist: {resourcesfile}"
            updated_dims.append([eval(dimname), resourcesfile])
        else:
            updated_dims.append([eval(dimname), details])
    return updated_dims

def get_ibm_diversescore_binary():
    return os.path.join(os.path.dirname(__file__), '..', 'ibm-diversescore', 'fast-downward.py')

def dump_plan_set(planset, dumpdir):
    os.makedirs(dumpdir, exist_ok=True)
    for i, plan in enumerate(planset):
        with open(os.path.join(dumpdir, f'sas_plan.{i+1}'), 'w') as f:
            f.write(f'{plan}')

def update_task_utilities(task):
    goals = {}
    for i, goal in enumerate(task.goals):
        i = i + 1
        if OperatorKind.AND == goal.node_type:
            for j, g in enumerate(goal.args):
                j = j + 1
                goals[g] = i * j
        else:
            goals[goal] = i * 2
    task.add_quality_metric(up.model.metrics.Oversubscription(goals))
    return goals
    