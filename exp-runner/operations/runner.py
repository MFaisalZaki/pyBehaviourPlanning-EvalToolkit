from collections import defaultdict
import json
import os
from datetime import datetime
import tempfile

import unified_planning as up
from unified_planning.shortcuts import get_environment
from unified_planning.io import PDDLReader
import up_symk
from unified_planning.shortcuts import Compiler, CompilationKind, OperatorKind

# from behaviour_planning.over_domain_models.smt.shortcuts import *
# from behaviour_planning.over_domain_models.ppltl.shortcuts import *

from up_behaviour_planning.FBIPlannerUp import FBIPlanner
import unified_planning as up
env = up.environment.get_environment()
env.factory.add_engine('FBIPlanner', __name__, 'FBIPlanner')

from .planners import FBISMTPlannerWrapper, FBIPPLTLPlannerWrapper, FIPlannerWrapper, SymKPlannerWrapper
from .planset_selectors import selection_using_first_k, selection_bspace, selection_maxsum
from .utilities import compute_maxsum_stability, compute_maxsum_states, replace_hyphens_in_pddl, update_task_utilities, experiment_reader, getkeyvalue, updatekeyvalue, construct_behaviour_space, updatekeyvalue
from .constants import *

def solve(args):
       
    results = {}
    expdetails = experiment_reader(args.experiment_file)
    
    try:
        result_file = getkeyvalue(expdetails, 'dump-result-file')
        failed_to_solvedir = os.path.join(os.path.dirname(result_file), 'failed-to-solve')
        os.makedirs(failed_to_solvedir, exist_ok=True)
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

        results = {}
        with tempfile.TemporaryDirectory(dir=expdetails['tmp-dir']) as tmpdirname:
            # Update task with oversubscription metric if the planning problem is utility-planning.
            up.shortcuts.get_environment().credits_stream = None
            up.shortcuts.get_environment().error_used_name = False
            task = PDDLReader().parse_problem(domain, problem)
            if getkeyvalue(expdetails, 'is-oversubscription-planning'):
                _goals = update_task_utilities(task)
                if len(_goals) < 2: expdetails['planner'] = 'SKIP'
            
            # Update behaviour space additional informaiton here.

            match expdetails['planner']:
                case 'fbippltl':
                    results = FBIPPLTLPlannerWrapper(args, task, expdetails)
                case 'fbismt':
                    results = FBISMTPlannerWrapper(args, task, expdetails)
                case 'fi':
                    results = FIPlannerWrapper(args, task, expdetails)
                case 'symk':
                    results = SymKPlannerWrapper(args, task, expdetails)

    except Exception as e:
        # Dump error to file.
        error_file = getkeyvalue(expdetails, 'error-file')
        assert error_file is not None, "Error file is not provided."
        with open(error_file, 'w') as f:
            f.write(str(e))
    finally:
        if len(results) > 0:
            if 'reason' in results:
                with open(os.path.join(failed_to_solvedir, os.path.basename(result_file)), 'w') as f:
                    json.dump(results, f, indent=4)
            else:
                # Dump results to json file.
                with open(result_file, 'w') as f:
                    json.dump(results, f, indent=4)

def score(args):
    diversity_scores_results = defaultdict(dict)
    expdetails = experiment_reader(args.experiment_file)
    
    results_dump_dir = os.path.join(os.path.dirname(args.experiment_file), '..', SCORE_DUMP_RESULTS)
    os.makedirs(results_dump_dir, exist_ok=True)

    tmp_dump_dir = os.path.join(os.path.dirname(args.experiment_file), '..', TMP_DUMP)
    os.makedirs(tmp_dump_dir, exist_ok=True)
    
    result_file = os.path.basename(args.experiment_file).replace('.json', f'-{args.k}-scores.json')
    result_file = os.path.join(results_dump_dir, result_file)
    try:

        # Now we need to construct the behaviour space for the diversity scores.
        domain  = getkeyvalue(expdetails, 'domainfile')
        problem = getkeyvalue(expdetails, 'problemfile')

        # Check if the task is oversubscription.
        is_oversubscription = getkeyvalue(expdetails, 'is-oversubscription')
        if is_oversubscription:
            # update the cost-bound-factor value to 1.0
            dims = getkeyvalue(expdetails, 'dims')
            for dimname, additional_info in dims:
                if dimname in ["UtilityDimension", "UtilitySet", "UtilityValue"]:
                    additional_info['cost-bound-factor'] = 1.0
            
            # assign the goal utilities.
            updatekeyvalue(expdetails, 'dims', dims)

        # It is better to construct the behaviour space from those dimensions.
        bspace_cfg = getkeyvalue(expdetails, 'bspace-cfg')
        if bspace_cfg is None: 
            bspace_cfg = {'k': args.k, 'dims': construct_behaviour_space(getkeyvalue(expdetails, 'planner'), getkeyvalue(expdetails, 'dims'))}
        else:
            updatekeyvalue(bspace_cfg, 'k', args.k)
            updatekeyvalue(bspace_cfg, 'dims', construct_behaviour_space(getkeyvalue(expdetails, 'planner'), getkeyvalue(expdetails, 'dims')))
        
        # check if the planner is fi or symk|fbi
        planlist = getkeyvalue(expdetails, 'plans')
        selection_method = getkeyvalue(expdetails, 'selection-method')
        plannername = getkeyvalue(expdetails, 'planner')
        
        match plannername:
            case 'fi':
                bspace_cfg['select-k'] = args.k
                tag = 'fi-bspace'
            case 'symk' | 'fbi' | 'fbi-ppltl':
                planlist = planlist[:args.k]
                tag = getkeyvalue(expdetails, 'tag')
            case _:
                assert False, f"Unknown planner: {getkeyvalue(expdetails, 'planner')}"

        diversity_scores_results['plans'] = planlist
        up.shortcuts.get_environment().credits_stream = None
        up.shortcuts.get_environment().error_used_name = False

        diversity_scores_results['diversity-scores'] = {'behaviour-count': 0}
        if len(planlist) > 0:
            # Based on the planner we need may want to apply a different selection strategy.
            if plannername in ['fbi-ppltl']:
                from behaviour_planning.over_domain_models.ppltl.bss.behaviour_count.behaviour_count import BehaviourCountPPLTL
                bspace = BehaviourCountPPLTL(domain, problem, bspace_cfg, planlist, is_oversubscription)
            else:
                from behaviour_planning.over_domain_models.smt.bss.behaviour_count.behaviour_count import BehaviourCountSMT
                # check if the planning problem is numeric then we need a different compilation list.
                # compilationlist=[['up_quantifiers_remover', CompilationKind.QUANTIFIERS_REMOVING], ['up_grounder', CompilationKind.GROUNDING]]
                
                # I hate this way but I have no other way to fix this.
                compilationlist = []
                if 'numeric' in result_file:
                    compilationlist = [['up_quantifiers_remover', CompilationKind.QUANTIFIERS_REMOVING], ['up_grounder', CompilationKind.GROUNDING]]
                else:
                    compilationlist = [['up_quantifiers_remover', CompilationKind.QUANTIFIERS_REMOVING], ['fast-downward-reachability-grounder', CompilationKind.GROUNDING]]
                
                bspace = BehaviourCountSMT(domain, problem, bspace_cfg, planlist, is_oversubscription, compilationlist)
            diversity_scores_results['diversity-scores'] = {'behaviour-count': bspace.count()}
            
        diversity_scores_results['info'] = {
            'domain':  getkeyvalue(expdetails, 'domain'),
            'problem': getkeyvalue(expdetails, 'problem'),
            'planner': getkeyvalue(expdetails, 'planner'),
            'tag': tag,
            'k': args.k,
            'q': getkeyvalue(expdetails, 'q')
        }
        selected_planslist = bspace.selected_plans(args.k)

        maxsum_stability = compute_maxsum_stability(selected_planslist)
        maxsum_states = compute_maxsum_states(bspace.task, selected_planslist)
        # compute_maxsum_stability(['\n'.join(map(str, plan.actions)) for plan in list(bspace.selected_plans)])
        diversity_scores_results['maxsum'] = (maxsum_stability + maxsum_states)/2
        diversity_scores_results['maxsum-stability'] = maxsum_stability
        diversity_scores_results['maxsum-states'] = maxsum_states

        pass

    except Exception as e:
        # Dump error to file.
        error_file = getkeyvalue(expdetails, 'error-file')
        if error_file is None:
            d = getkeyvalue(expdetails, 'domain')
            p = getkeyvalue(expdetails, 'problem')
            error_file = os.path.join(os.path.dirname(args.experiment_file), '..', 'score-run-error', f'{d}-{p}')
            os.makedirs(os.path.dirname(error_file), exist_ok=True)
        assert error_file is not None, "Error file is not provided."
        with open(error_file, 'w') as f:
            f.write(str(e))
    finally:        
        # Dump results to json file.
        with open(result_file, 'w') as f:
            json.dump(diversity_scores_results, f, indent=4)
