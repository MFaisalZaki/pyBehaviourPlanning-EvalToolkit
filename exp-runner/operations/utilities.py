from collections import defaultdict
from copy import deepcopy
import os
import json
import importlib.util

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
    return expdetails

def parse_planning_tasks(planningtasksdir:str, resourcesfiledir:str, resourcesdumpdir:str):
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
            for no, problem in enumerate(domainsproblems[0]['problems']):
                _instanceno = no+1
                planning_problem                = defaultdict(dict)
                planning_problem['domainname']  = _domainname
                planning_problem['instanceno']  = _instanceno
                planning_problem['ipc_year']    = _ipc_year
                planning_problem['domainfile']  = os.path.join(os.path.dirname(domainsroot), problem[0])
                planning_problem['problemfile'] = os.path.join(os.path.dirname(domainsroot), problem[1])

                # check if the domain and problem instance has resources.
                if _ipc_year in resources and _domainname in resources[_ipc_year]:
                    if str(_instanceno) in resources[_ipc_year][_domainname]:
                        planning_problem['resources'] = resources[_ipc_year][_domainname][str(_instanceno)]
                        # maybe I'll consider this later.
                        # dump the resources to a file. 
                        resourcesfile = os.path.join(resourcesdumpdir, f'{_domainname}_{_instanceno}_resources.txt')
                        with open(resourcesfile, 'w') as f:
                            f.write(planning_problem['resources'])

                # Ignore if the domain or problem file does not exist.
                if not (os.path.exists(planning_problem['domainfile']) and os.path.exists(planning_problem['problemfile'])): continue
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

def construct_run_cmd(experiment_file):
    cmd = "solve "
    cmd += f" --experiment-file {experiment_file}"

    # cmd += f"--domainname {planningtask['domainname']} "
    # cmd += f"--instanceno {planningtask['instanceno']} "
    # cmd += f"--ipc-year {planningtask['ipc_year']} "
    # cmd += f"--planner-cfg-file {plannercfg} "
    # cmd += f"--exp-details-dir {expdetailsfile} "
    # cmd += f"--run-dir {rundir} "
    # cmd += f"--domain {planningtask['domainfile']} "
    # cmd += f"--problem {planningtask['problemfile']} "
    # cmd += f"--results-dump-dir {dump_results_dir} "
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

def createVEnv(basedir, requirements_file):
    venv_dir = os.path.join(basedir, 'v-env')
    os.makedirs(venv_dir, exist_ok=True)
    ## start a venv and install the required packages.
    os.system(f'python3 -m venv {venv_dir}')
    os.system(f'{venv_dir}/bin/python3 -m pip install -r {requirements_file}')
    return venv_dir
