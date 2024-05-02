from collections import defaultdict
import json
import os

import os, sys
sys.path.append('/home/ma342/developer/pyBehaviourPlanningEvalToolkit/external-pkgs/pyBehaviourSortsSuite')
sys.path.append('/home/ma342/developer/pyBehaviourPlanningEvalToolkit/external-pkgs/pyBehaviourSortsSuite/bss')

from unified_planning.shortcuts import OneshotPlanner, get_environment
from unified_planning.io import PDDLReader, PDDLWriter
import up_symk

from fbi.shortcuts import *
from bss.shortcuts import *

from .utilities import experiment_reader, getkeyvalue, updatekeyvalue, construct_behaviour_space, read_planner_cfg, update_fbi_parameters, generate_summary_file
from .constants import *

def solve(args):
#     # I guess the best way to do so is by using the UPWrapper.
#     # But note that now we don't have a unified wrapper since the the fbi one returns
#     # a list of two stuff. So this one will be a little bit messy.
    get_environment().credits_stream  = None
    get_environment().error_used_name = False
    
    results = {}
    expdetails = experiment_reader(args.experiment_file)
    try:
        result_file = getkeyvalue(expdetails, 'dump-result-file')
        assert result_file is not None, "Result file is not provided."
        if os.path.exists(result_file):
            # move this to another directory.
            repeated_results_dir = os.path.join(os.path.dirname(result_file), 'repeated-results')
            os.makedirs(repeated_results_dir, exist_ok=True)
            os.rename(result_file, os.path.join(repeated_results_dir, os.path.basename(result_file)))
            pass
        assert not os.path.exists(result_file), "Result file already exists."
        
        domain = getkeyvalue(expdetails, 'domainfile')
        problem = getkeyvalue(expdetails, 'problemfile')
        assert domain is not None and problem is not None, "Domain or problem file is not provided."
        task = PDDLReader().parse_problem(domain, problem)

        planner_params = read_planner_cfg(args.experiment_file)

        match expdetails['planner']:
            case 'fbi':
                # Update the behaviour space with the resources file if exists.
                planner_params = update_fbi_parameters(planner_params, expdetails)
                with OneshotPlanner(name='FBIPlanner',  params=planner_params) as planner:
                    result = planner.solve(task)
                planlist = [r.plan for r in result[0]]
                logmsgs  = result[1]
                # This is hacky by I have no time to properly fix this shit.
                updatekeyvalue(planner_params, 'dims', [[d.__name__, af] for d, af in getkeyvalue(planner_params, 'dims')])
                # this should be moved to a function
                results = generate_summary_file(task, expdetails, 'FBIPlanner', planner_params, domain, problem, planlist, logmsgs)
            case 'fi':
                pass
            case 'symk':
                pass
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

        planlist = getkeyvalue(expdetails, 'plans')[:args.k]
        diversity_scores_results['plans'] = planlist

        # Now we need to construct the behaviour space for the diversity scores.
        domain = getkeyvalue(expdetails, 'domainfile')
        problem = getkeyvalue(expdetails, 'problemfile')

        # It is better to construct the behaviour space from those dimensions.
        bspace_cfg = getkeyvalue(expdetails, 'bspace-cfg')
        updatekeyvalue(bspace_cfg, 'k', args.k)
        updatekeyvalue(bspace_cfg, 'dims', construct_behaviour_space(getkeyvalue(expdetails, 'dims')))

        bspace = BehaviourCount(domain, problem, bspace_cfg, planlist)

        diversity_scores_results['info'] = {
            'domain': domain,
            'problem': problem,
            'k': args.k
        }

        diversity_scores_results['diversity-scores'] = {'behaviour-count': bspace.count()}
        
    except Exception as e:
        # Dump error to file.
        error_file = getkeyvalue(expdetails, 'error-file') + '-score.json'
        assert error_file is not None, "Error file is not provided."
        with open(error_file, 'w') as f:
            f.write(str(e))
    finally:
        
        # Dump results to json file.
        with open(result_file, 'w') as f:
            json.dump(diversity_scores_results, f, indent=4)
    pass


