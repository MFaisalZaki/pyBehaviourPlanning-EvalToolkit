import json
import os 
import sys
import subprocess

from unified_planning.io import PDDLReader

from behaviour_planning.over_domain_models.smt.bss.behaviour_space.space_encoders.basic import BehaviourSpaceSMT
from .utilities import getkeyvalue, update_fbi_parameters, dump_plan_set, get_ibm_diversescore_binary


def selection_using_first_k(k, _planlist):
    return _planlist[:k] if len(_planlist) > k else _planlist

def selection_maxsum(args, k, _planlist, _tmprun):
    if len(_planlist) <= k: return _planlist
    
    with open(args.experiment_file, 'r') as exp_details_file:
        exp_details = json.load(exp_details_file)
    
    domainfile        = getkeyvalue(exp_details, 'domainfile')
    problemfile       = getkeyvalue(exp_details, 'problemfile')
    metric            = 'stability'
    
    domainname = os.path.basename(os.path.dirname(domainfile)).split('.')[0]
    problemname = os.path.basename(problemfile).split('.')[0]


    plans_dump_dir    = os.path.join(_tmprun, f'{domainname}-{problemname}-{k}-fi-maxsum-plans-dump')
    score_run_dir     = os.path.join(_tmprun, f'{domainname}-{problemname}-{k}-fi-maxsum-score-run')
    
    # first dump the plans to a directory in sas file format.
    dump_plan_set(_planlist, plans_dump_dir)

    # construct the score command for the IBM diverse score.
    score = f"subset(compute_{metric.lower()}_metric=true,aggregator_metric=avg,plans_as_multisets=false,plans_subset_size={k},exact_method=false,similarity=false,reduce_labels=false,dump_plans=true)"
    cmd = [sys.executable, 
            get_ibm_diversescore_binary(), 
            domainfile, 
            problemfile, 
            "--diversity-score", score, 
            "--internal-plan-files-path", plans_dump_dir, 
            "--internal-num-plans-to-read", str(len(_planlist))]
    
    # select plans based on the stability metric.
    os.makedirs(score_run_dir, exist_ok=True)
    result = subprocess.check_output(cmd, universal_newlines=True, cwd=score_run_dir)

    # read the selected plans from the score_run_dir.
    selected_plans = []
    for plan in os.listdir(score_run_dir):
        with open(os.path.join(score_run_dir, plan), 'r') as f:
            selected_plans.append(f.read())    
    return selected_plans

def selection_bspace(_args, k, _planlist):
    with open(_args.experiment_file, 'r') as exp_details_file:
        exp_details = json.load(exp_details_file)
    
    domainfile  = getkeyvalue(exp_details, 'domainfile')
    problemfile = getkeyvalue(exp_details, 'problemfile')
    
    _task = PDDLReader().parse_problem(domainfile, problemfile)
    exp_details['base-planner-cfg'] = {'k': k }
    exp_details['bspace-cfg'] = {'quality-bound-factor': 1.0}
    cfg = update_fbi_parameters(exp_details, exp_details)

    # convert the plan list to a list of SequentialPlan objects.
    planlist = [PDDLReader().parse_plan_string(_task, p) for p in _planlist]

    # compute upper bound.
    upper_bound = max([len(p.actions) for p in planlist])
    cfg['encoder']     = 'qfuf' 
    cfg['upper-bound'] = upper_bound
    cfg['run-plan-validation'] = False
    cfg['disable-after-goal-state-actions'] = True
    cfg['is-oversubscription-planning'] = False

    # create the behaviour space.
    bspace = BehaviourSpaceSMT(_task, cfg)

    # now optimise on the behaviour count.
    covered_behaviours = set()
    selected_plans = []
    for i, plan in enumerate(planlist):
        if len(covered_behaviours) > k: break
        ret = bspace.plan_behaviour(plan, i)
        if ret.behaviour in covered_behaviours: continue
        covered_behaviours.add(ret.behaviour)
        selected_plans.append(str(ret))
    return selected_plans

