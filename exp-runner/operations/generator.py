import os
from copy import deepcopy
import json

from .utilities import parse_planning_tasks, parse_experiment_details, construct_run_cmd, warpCommand, getkeyvalue

def generate(args):
    # create the experiment folders.
    generated_cmds_dir = os.path.join(args.sandbox_dir, 'experiment_tasks')
    planners_run_dir   = os.path.join(args.sandbox_dir, 'planners_run')
    dump_results_dir   = os.path.join(args.sandbox_dir, 'dump_results')
    slurm_scripts_dir  = os.path.join(args.sandbox_dir, 'slurm_scripts')
    resources_dump_dir = os.path.join(args.sandbox_dir, 'resources_dump')
    error_dir          = os.path.join(args.sandbox_dir, 'run_errors')
    for dir_ in  [args.sandbox_dir, planners_run_dir, dump_results_dir, generated_cmds_dir, slurm_scripts_dir, resources_dump_dir, error_dir]:
        os.makedirs(dir_, exist_ok=True)
    # Read the experiment details.
    expdetails = parse_experiment_details(args.exp_details_dir)
    # Parse the planning tasks dir.
    selected_planning_tasks = getkeyvalue(expdetails, 'selected-planning-instances')
    planning_tasks = parse_planning_tasks(args.planning_tasks_dir, getkeyvalue(expdetails, 'resources-file-dir'), resources_dump_dir, selected_planning_tasks)
    generated_cmds = set()
    venv_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'v-env')
    qlist = getkeyvalue(expdetails, 'q')
    klist = getkeyvalue(expdetails, 'k')
    plannerslist = getkeyvalue(expdetails, 'planners')
    skip_cfgs = getkeyvalue(expdetails, 'skip-cfgs')
    for taskidx, planning_task in enumerate(planning_tasks):
        for q in qlist:
            for k in klist:
                for plannername, plannercfg in plannerslist.items():
                    if (q, k , plannername) in skip_cfgs: 
                        continue
                    print(f"Generating tasks for q={q}, k={k}, planner={plannername}: {taskidx}/{len(planning_tasks)}")
                    task = deepcopy(planning_task)
                    task['k'] = k
                    task['q'] = q
                    task['planner']          = plannername
                    task['planner-cfg']      = plannercfg
                    task['dump-results-dir'] = dump_results_dir
                    
                    filename = f"{task['ipc_year']}-{task['domainname']}-{task['instanceno']}-{q}-{k}-{plannername}"
                    task['error-file']       = os.path.join(error_dir, filename)
                    # generate a unique task run directory.
                    rundir = os.path.join(planners_run_dir, filename)
                    os.makedirs(rundir, exist_ok=True)

                    # Save task json file to the dump directory.
                    task_jsonfile = os.path.join(generated_cmds_dir, f"{task['ipc_year']}-{task['domainname']}-{task['instanceno']}-{q}-{k}-{plannername}.json")
                    with open(task_jsonfile, 'w') as f:
                        json.dump(task, f, indent=4)

                    cmd = construct_run_cmd(task_jsonfile)
                    generated_cmds.add(f'source {venv_dir}/bin/activate && cd {rundir} && {cmd} && deactivate')

    # dump those commands to a file.
    with open(os.path.join(generated_cmds_dir, 'generated_cmds.sh'), 'w') as f:
        for cmd in generated_cmds:
            f.write(f'{cmd}\n')
    # No split the commands in to strum batch script files.
    for i, cmd in enumerate(generated_cmds):
        slurmcmd = warpCommand(cmd, getkeyvalue(expdetails, 'timelimit'), getkeyvalue(expdetails, 'memorylimit'), slurm_scripts_dir, args.partition)
        with open(os.path.join(slurm_scripts_dir, f'slurm_batch_task_{i}.txt'), 'w') as f:
            f.write(slurmcmd)