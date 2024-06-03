import tempfile
import os
import json
import sys
import subprocess
import logging
from subprocess import SubprocessError

from unified_planning.engines import PlanGenerationResultStatus as ResultsStatus
from unified_planning.shortcuts import OneshotPlanner, AnytimePlanner



from .utilities import update_fbi_parameters, generate_summary_file, updatekeyvalue, getkeyvalue, read_planner_cfg

def FBIPlannerWrapper(args, task, expdetails):
    # Update the behaviour space with the resources file if exists.
    planner_params = read_planner_cfg(args.experiment_file)
    planner_params = update_fbi_parameters(planner_params, expdetails)
    with OneshotPlanner(name='FBIPlanner',  params=planner_params) as planner:
        result = planner.solve(task)
    if len(result) == 0: 
        return {'reason': 'No plans found by fbi'}
    planlist = [r.plan for r in result[0]]
    logmsgs  = result[1]
    # This is hacky by I have no time to properly fix this shit.
    updatekeyvalue(planner_params, 'dims', [[d.__name__, af] for d, af in getkeyvalue(planner_params, 'dims')])
    
    results = generate_summary_file(task, expdetails, 'fbi', planner_params, planlist, logmsgs)
    return results

def FIPlannerWrapper(args, task, expdetails):

    def _selection_using_first_k(k, _planlist):
        return _planlist[:k] if len(_planlist) > k else _planlist
    
    def _selection_maxsum(args, task, k, _planlist):
        if len(_planlist) <= k: return _planlist
        pass


    cmd  = [sys.executable]
    cmd += ["-m"]
    cmd += ["forbiditerative.plan"]
    cmd += ["--planner"]
    cmd += ["extended_unordered_topq"]
    cmd += ["--domain"]
    cmd += [getkeyvalue(expdetails, 'domainfile')]
    cmd += ["--problem"]
    cmd += [getkeyvalue(expdetails, 'problemfile')]
    cmd += ["--number-of-plans"]
    cmd += [str(getkeyvalue(expdetails, 'k'))]
    cmd += ["--quality-bound"]
    cmd += [str(getkeyvalue(expdetails, 'q'))]
    cmd += ["--symmetries"]
    cmd += ["--use-local-folder"]
    cmd += ["--clean-local-folder"]
    cmd += ["--suppress-planners-output"]
    

    tmpdir = getkeyvalue(expdetails, 'tmp-dir')
    tmprun = os.path.join(tmpdir, 'tmp-run-dir')
    os.makedirs(tmprun, exist_ok=True)

    fienv = os.environ.copy()
    fienv['FI_PLANNER_RUNS'] = tmprun
    try:
        output = subprocess.check_output(cmd, env=fienv, cwd=tmpdir)
    except SubprocessError as e:
        pass
    finally:
        planlist = []
        found_plans = os.path.join(tmpdir, 'found_plans', 'done')
        if not os.path.exists(found_plans): return {'reason': 'No plans found by fi'}
        for plan in os.listdir(found_plans):
            with open(os.path.join(found_plans, plan), 'r') as f:
                planlist.append(f.read())
        
        # select plans based on the selection criteria.
        with open(getkeyvalue(expdetails, 'planner-cfg'), 'r') as f:
            planner_cfg = json.load(f)
        selection_method = getkeyvalue(planner_cfg, 'selection-method')

        match selection_method:
            case 'first-k':
                planlist = _selection_using_first_k(getkeyvalue(expdetails, 'k'), planlist)
            case 'bspace':
                pass
            case 'maxsum':
                pass
            case _:
                assert False, f"Unknown selection method: {selection_method}"

        planner_params = read_planner_cfg(args.experiment_file)
        results = generate_summary_file(task, expdetails, 'fi', planner_params, planlist, [])

        




        return results

def SymKPlannerWrapper(args, task, expdetails):
    planlist = []
    k = getkeyvalue(expdetails, 'k')
    q = getkeyvalue(expdetails, 'q')
    search_config = f"symq-bd(plan_selection=top_k(num_plans={k},dump_plans=true),quality={q})"
    tmpdir = getkeyvalue(expdetails, 'tmp-dir')

    with tempfile.TemporaryDirectory(dir=tmpdir) as tmpdirname:        
        with AnytimePlanner(name='symk-opt', params={"symk_anytime_search_config": search_config}) as planner:
            for i, result in enumerate(planner.get_solutions(task)):
                if result.status == ResultsStatus.INTERMEDIATE:
                    planlist.append(result.plan) if i < k else None
    
    planner_params = read_planner_cfg(args.experiment_file)
    results = generate_summary_file(task, expdetails, 'symk', planner_params, planlist, [])
    return results