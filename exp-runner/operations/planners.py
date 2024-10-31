import tempfile
import os
import json
import sys
import subprocess
import logging
from subprocess import SubprocessError
from copy import deepcopy
from unified_planning.engines import PlanGenerationResultStatus as ResultsStatus
from unified_planning.shortcuts import OneshotPlanner, AnytimePlanner

from behaviour_planning.over_domain_models.smt.shortcuts import *
from .planset_selectors import selection_using_first_k, selection_maxsum, selection_bspace

from .utilities import (
    update_fbi_parameters, 
    generate_summary_file, 
    updatekeyvalue, 
    getkeyvalue, 
    read_planner_cfg,
    dump_plan_set,
    get_ibm_diversescore_binary
)

def FBISMTPlannerWrapper(args, task, expdetails):
    # Update the behaviour space with the resources file if exists.
    planner_params = read_planner_cfg(args.experiment_file)
    dimensions_cpy = getkeyvalue(planner_params, 'dims')
    planner_params = update_fbi_parameters(planner_params, expdetails)
    with OneshotPlanner(name='FBIPlanner',  params=deepcopy(planner_params)) as planner:
        result = planner.solve(task)
    if len(result[0]) <= 1: 
        return {'reason': 'No plans found by fbi'}
    planlist = [r.plan for r in result[0]]
    planlist = list(filter(lambda p: not p is None, planlist))
    logmsgs  = result[1]
    planner_params['bspace-cfg']['dims'] = dimensions_cpy
    results = generate_summary_file(task, expdetails, 'fbi', planner_params, planlist, logmsgs)
    return results

def FIPlannerWrapper(args, task, expdetails):
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
                planlist = selection_using_first_k(getkeyvalue(expdetails, 'k'), planlist)
            case 'bspace':
                planlist = selection_bspace(args, task, getkeyvalue(expdetails, 'k'), planlist)
            case 'maxsum':
                planlist = selection_maxsum(args, getkeyvalue(expdetails, 'k'), planlist, tmprun)
            case 'none':
                planlist = planlist
            case _:
                assert False, f"Unknown selection method: {selection_method}"

        planner_params = read_planner_cfg(args.experiment_file)
        results = generate_summary_file(task, expdetails, 'fi', planner_params, planlist, [])

        return results

def SymKPlannerWrapper(args, task, expdetails):

    planlist = []
    k = getkeyvalue(expdetails, 'k')
    q = getkeyvalue(expdetails, 'q')
    tmpdir = getkeyvalue(expdetails, 'tmp-dir')

    if getkeyvalue(expdetails, 'is-oversubscription-planning'):
        tmpdir_onshot = os.path.join(tmpdir, 'tmp-onshot-dir')
        os.makedirs(tmpdir_onshot, exist_ok=True)
        oversubscription_metric = task.quality_metrics.pop()
        # solve the planning problem first without the oversubscription metric.
        cost_bound = None
        with tempfile.TemporaryDirectory(dir=tmpdir_onshot) as tmpdirname:        
            with OneshotPlanner(name="symk-opt") as planner:
                result = planner.solve(task)
                plan = result.plan
                assert plan is not None, "No plan found by symk"
                cost_bound = int(len(plan.actions) * getkeyvalue(expdetails, 'cost-bound-factor'))
        # now remove the hard goals then generate k plans with different utilities.
        _ = task.goals.pop()
        task.add_quality_metric(oversubscription_metric)
        tmpdir_anytime = os.path.join(tmpdir, 'tmp-anytime-dir')
        os.makedirs(tmpdir_anytime, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=tmpdir_anytime) as tmpdirname:        
            with AnytimePlanner(name='symk', params={"plan_cost_bound": cost_bound, "number_of_plans": k}) as planner:
                for i, result in enumerate(planner.get_solutions(task)):
                    if result.status == ResultsStatus.INTERMEDIATE:
                        planlist.append(result.plan) if i < k else None
            # remove empty plans.
            planlist = list(filter(lambda p: len(p.actions) > 0, planlist))
    else:
        search_config = f"symq-bd(plan_selection=top_k(num_plans={k},dump_plans=true),quality={q})"
        with tempfile.TemporaryDirectory(dir=tmpdir) as tmpdirname:        
            with AnytimePlanner(name='symk-opt', params={"symk_anytime_search_config": search_config}) as planner:
                for i, result in enumerate(planner.get_solutions(task)):
                    if result.status == ResultsStatus.INTERMEDIATE:
                        planlist.append(result.plan) if i < k else None

    planner_params = read_planner_cfg(args.experiment_file)
    results = generate_summary_file(task, expdetails, 'symk', planner_params, planlist, [])
    return results