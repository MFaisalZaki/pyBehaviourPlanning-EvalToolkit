from collections import defaultdict
import json
import os

from unified_planning.shortcuts import OneshotPlanner
from unified_planning.io import PDDLReader, PDDLWriter
import up_symk
from fbi.shortcuts import *

from .utilities import experiment_reader, getkeyvalue, updatekeyvalue, read_planner_cfg, update_fbi_parameters, generate_summary_file

def solve(args):
#     # I guess the best way to do so is by using the UPWrapper.
#     # But note that now we don't have a unified wrapper since the the fbi one returns
#     # a list of two stuff. So this one will be a little bit messy.
    results = {}
    expdetails = experiment_reader(args.experiment_file)
    try:
        result_file = getkeyvalue(expdetails, 'dump-result-file')
        assert result_file is not None, "Result file is not provided."
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

    pass


