import os
from copy import deepcopy
import json

from .utilities import parse_planning_tasks, parse_experiment_details, construct_solve_cmd, construct_score_cmd, warpCommand, getkeyvalue
from .constants import *


def generate(args):
    venv_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'v-env')
    if args.for_score_exp:generate_score_cmds(args, venv_dir)
    else: generate_solve_cmds(args, venv_dir)

def generate_score_cmds(args, venv_dir):
    # Read the experiment details.
    expdetails = parse_experiment_details(args.exp_details_dir)
    # Create the experiment folders.
    run_score_dir = os.path.join(args.sandbox_dir, SCORES_RESULTS_RUN)
    os.makedirs(run_score_dir, exist_ok=True)
    # Create a directory to dump the results into.
    scores_results = os.path.join(args.sandbox_dir, SCORES_RESULTS)
    os.makedirs(scores_results, exist_ok=True)
    # Check the directory containing the experiment results.
    generated_cmds = set()
    results_dir = os.path.join(args.sandbox_dir, DUMP_RESULTS)
    for results in os.listdir(results_dir):
        if not results.endswith('.json'): continue
        # read the number of plans available in the results file.
        results_file = os.path.join(results_dir, results)
        with open(results_file, 'r') as f:
            results = json.load(f)
            plans = getkeyvalue(results, 'plans')
            if plans is None: continue
            no_plans = len(plans)
            for k in args.score_for_k:
                if k > no_plans: break
                cmd = construct_score_cmd(k, results_file)
                rundir = os.path.join(run_score_dir, f'score-{os.path.basename(results_file)}-k-{k}')
                os.makedirs(rundir, exist_ok=True)
                generated_cmds.add(f'source {venv_dir}/bin/activate && cd {rundir} && {cmd} && deactivate')

    # dump those commands to a file.
    generated_cmds_dir = os.path.join(args.sandbox_dir, SCORES_RESULTS_CMD)
    os.makedirs(generated_cmds_dir, exist_ok=True)
    with open(os.path.join(generated_cmds_dir, 'score-cmds.sh'), 'w') as f:
        for cmd in generated_cmds:
            f.write(f'{cmd}\n')
    
    # Now split the commands in to strum batch script files.
    slurm_dump_logs = os.path.join(args.sandbox_dir, SLURM_SCORE_LOGS)
    os.makedirs(slurm_dump_logs, exist_ok=True)
    slurm_cmds = os.path.join(args.sandbox_dir, SLURM_SCORE_SCRIPTS)
    os.makedirs(slurm_cmds, exist_ok=True)
    for i, cmd in enumerate(generated_cmds):
        slurmcmd = warpCommand(cmd, getkeyvalue(expdetails, 'timelimit'), getkeyvalue(expdetails, 'memorylimit'), slurm_dump_logs, args.partition)
        with open(os.path.join(slurm_cmds, f'slurm_batch_task_{i}.txt'), 'w') as f:
            f.write(slurmcmd)

def generate_solve_cmds(args, venv_dir):
    # create the experiment folders.
    generated_cmds_dir = os.path.join(args.sandbox_dir, EXPS_TASKS)
    planners_run_dir   = os.path.join(args.sandbox_dir, PLANNERS_RUN)
    dump_results_dir   = os.path.join(args.sandbox_dir, DUMP_RESULTS)
    slurm_solve_scripts_dir  = os.path.join(args.sandbox_dir, SLURM_SOLVE_SCRIPTS)
    slurm_dump_logs    = os.path.join(args.sandbox_dir, SLURM_SOLVE_LOGS)
    resources_dump_dir = os.path.join(args.sandbox_dir, RESOURCES_DUMP)
    error_dir          = os.path.join(args.sandbox_dir, ERRORS_SOLVE)
    tmp_dir            = os.path.join(args.sandbox_dir, TMP_DIR)
    for dir_ in  [args.sandbox_dir, planners_run_dir, dump_results_dir, generated_cmds_dir, slurm_solve_scripts_dir, resources_dump_dir, error_dir, slurm_dump_logs, tmp_dir]:
        os.makedirs(dir_, exist_ok=True)
    # Read the experiment details.
    expdetails = parse_experiment_details(args.exp_details_dir)
    # Parse the planning tasks dir.
    selected_planning_tasks = getkeyvalue(expdetails, 'selected-planning-instances')
    planning_tasks = parse_planning_tasks(args.planning_tasks_dir, getkeyvalue(expdetails, 'resources-file-dir'), resources_dump_dir, selected_planning_tasks)
    generated_cmds = set()
    # Read the planners list.
    plannerslist = []
    for plannername, plannercfg in getkeyvalue(expdetails, 'planners').items():
        with open(plannercfg, 'r') as f:
            data = json.load(f)
            plannerslist.append((plannername, getkeyvalue(data, 'tag'), plannercfg))
    qlist = getkeyvalue(expdetails, 'q')
    klist = getkeyvalue(expdetails, 'k')
    skip_cfgs = getkeyvalue(expdetails, 'skip-cfgs')
    for taskidx, planning_task in enumerate(planning_tasks):
        for q in qlist:
            for k in klist:
                for plannername, tag, plannercfg in plannerslist:
                    if (q, k , plannername) in skip_cfgs: 
                        continue
                    print(f"Generating tasks for q={q}, k={k}, planner={plannername}: {taskidx}/{len(planning_tasks)}")
                    task = deepcopy(planning_task)
                    task['k'] = k
                    task['q'] = q
                    task['planner']     = plannername
                    task['planner-cfg'] = plannercfg
                    task['tag']         = tag

                    filename = f"{task['ipc_year']}-{task['domainname']}-{task['instanceno']}-{q}-{k}-{plannername}"
                    task['dump-result-file'] = os.path.join(dump_results_dir, f'{filename}.json')
                    task['error-file']       = os.path.join(error_dir, f'{filename}.error')
                    task['tmp-dir']          = os.path.join(tmp_dir, filename)
                    # generate a unique task run directory.
                    rundir = os.path.join(planners_run_dir, filename)
                    os.makedirs(rundir, exist_ok=True)
                    os.makedirs(task['tmp-dir'], exist_ok=True)

                    # Save task json file to the dump directory.
                    task_jsonfile = os.path.join(generated_cmds_dir, f"{filename}.json")
                    with open(task_jsonfile, 'w') as f:
                        json.dump(task, f, indent=4)

                    cmd = construct_solve_cmd(task_jsonfile)
                    generated_cmds.add(f'source {venv_dir}/bin/activate && cd {rundir} && {cmd} && deactivate')

    # Dump those commands to a file.
    with open(os.path.join(generated_cmds_dir, 'solve-cmds.sh'), 'w') as f:
        for cmd in generated_cmds:
            f.write(f'{cmd}\n')
    # Now split the commands in to strum batch script files.
    for i, cmd in enumerate(generated_cmds):
        slurmcmd = warpCommand(cmd, getkeyvalue(expdetails, 'timelimit'), getkeyvalue(expdetails, 'memorylimit'), slurm_dump_logs, args.partition)
        with open(os.path.join(slurm_solve_scripts_dir, f'slurm_batch_task_{i}.txt'), 'w') as f:
            f.write(slurmcmd)