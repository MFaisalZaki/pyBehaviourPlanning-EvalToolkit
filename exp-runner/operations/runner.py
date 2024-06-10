from collections import defaultdict
import json
import os
from datetime import datetime

import unified_planning as up
from unified_planning.shortcuts import get_environment
from unified_planning.io import PDDLReader
import up_symk

from behaviour_planning.over_domain_models.smt.shortcuts import *

from .planners import FBIPlannerWrapper, FIPlannerWrapper, SymKPlannerWrapper

from .utilities import experiment_reader, getkeyvalue, updatekeyvalue, construct_behaviour_space
from .constants import *

def solve(args):
    
    
    results = {}
    expdetails = experiment_reader(args.experiment_file)
    try:
        result_file = getkeyvalue(expdetails, 'dump-result-file')
        assert result_file is not None, "Result file is not provided."
        if os.path.exists(result_file):
            # move this to another directory.
            repeated_results_dir = os.path.join(os.path.dirname(result_file), '..', 'repeated-results')
            os.makedirs(repeated_results_dir, exist_ok=True)
            # get current time and date.
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(result_file, os.path.join(repeated_results_dir, f'{os.path.basename(result_file)}-{timestamp}'))
            pass
        assert not os.path.exists(result_file), "Result file already exists."
        
        domain  = getkeyvalue(expdetails, 'domainfile')
        problem = getkeyvalue(expdetails, 'problemfile')
        assert domain is not None and problem is not None, "Domain or problem file is not provided."
        
        get_environment().credits_stream  = None
        get_environment().error_used_name = False
        
        # Update task with oversubscription metric if the planning problem is utility-planning.
        task = PDDLReader().parse_problem(domain, problem)
        if getkeyvalue(expdetails, 'is-oversubscription-planning'):
            goals = {}
            for i, goal in enumerate(task.goals):
                i = i + 1
                for j, g in enumerate(goal.args):
                    j = j + 1
                    goals[g] = i * j
            task.add_quality_metric(up.model.metrics.Oversubscription(goals))

        match expdetails['planner']:
            case 'fbi':
                results = FBIPlannerWrapper(args, task, expdetails)
            case 'fi':
                results = FIPlannerWrapper(args, task, expdetails)
            case 'symk':
                results = SymKPlannerWrapper(args, task, expdetails)

        # check if the behaviour count is required to be compute.
        if expdetails['compute-behaviour-count']:
            k_list = expdetails['behaviour-count-k-list']
            if len(k_list) == 0: k_list = [expdetails['k']]

            planlist = [PDDLReader().parse_plan_string(task, p) for p in results['plans']]

            # compute upper bound.
            upper_bound = max([len(p.actions) for p in planlist])
            cfg = dict()
            cfg['encoder']     = 'qfuf' 
            cfg['upper-bound'] = upper_bound
            cfg['run-plan-validation'] = False
            cfg['disable-after-goal-state-actions'] = True
            cfg['is-oversubscription-planning'] = False
            cfg['dims'] = construct_behaviour_space(getkeyvalue(expdetails, 'dims'))

            diversity_scores_results = {k: 0 for k in k_list}
            bspace = BehaviourSpace(task, cfg)
            
            for k in k_list:
                if k > len(planlist): break
                match expdetails['planner']:
                    case 'fbi' | 'symk':
                        top_k_plans = planlist[:k] 
                    case 'fi':
                        top_k_plans = planlist
                collected_behaviours = set()
                for i, plan in enumerate(top_k_plans):
                    ret = bspace.plan_behaviour(plan, i)
                    collected_behaviours.add(ret.behaviour)
                diversity_scores_results[k] = len(collected_behaviours)
            
            results['diversity-scores'] = {'behaviour-count': diversity_scores_results}

    except Exception as e:
        # Dump error to file.
        error_file = getkeyvalue(expdetails, 'error-file')
        assert error_file is not None, "Error file is not provided."
        with open(error_file, 'w') as f:
            f.write(str(e))
    finally:
        if len(results) > 0:
            # Dump results to json file.
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=4)


def score(args):
    diversity_scores_results = defaultdict(dict)
    expdetails = experiment_reader(args.experiment_file)
    
    results_dump_dir = os.path.join(os.path.dirname(args.experiment_file), '..', SCORES_RESULTS)
    os.makedirs(results_dump_dir, exist_ok=True)

    result_file = os.path.basename(args.experiment_file).replace('.json', f'-{args.k}-scores.json')
    result_file = os.path.join(results_dump_dir, result_file)
    try:

        # Now we need to construct the behaviour space for the diversity scores.
        domain = getkeyvalue(expdetails, 'domainfile')
        problem = getkeyvalue(expdetails, 'problemfile')

        # It is better to construct the behaviour space from those dimensions.
        bspace_cfg = getkeyvalue(expdetails, 'bspace-cfg')
        updatekeyvalue(bspace_cfg, 'k', args.k)
        updatekeyvalue(bspace_cfg, 'dims', construct_behaviour_space(getkeyvalue(expdetails, 'dims')))

        # Based on the planner we need may want to apply a different selection strategy.
        planlist = getkeyvalue(expdetails, 'plans')[:args.k]
        diversity_scores_results['plans'] = planlist

        bspace = BehaviourCount(domain, problem, bspace_cfg, planlist)

        diversity_scores_results['info'] = {
            'domain':  getkeyvalue(expdetails, 'domain'),
            'problem': getkeyvalue(expdetails, 'problem'),
            'planner': getkeyvalue(expdetails, 'planner'),
            'tag': getkeyvalue(expdetails, 'tag'),
            'k': args.k,
            'q': getkeyvalue(expdetails, 'q')
        }

        diversity_scores_results['diversity-scores'] = {'behaviour-count': bspace.count()}
        
    except Exception as e:
        # Dump error to file.
        error_file = os.path.basename(args.experiment_file).replace('.json', f'-{args.k}-scores.error')
        assert error_file is not None, "Error file is not provided."
        with open(error_file, 'w') as f:
            f.write(str(e))
    finally:
        
        # Dump results to json file.
        with open(result_file, 'w') as f:
            json.dump(diversity_scores_results, f, indent=4)
    pass


