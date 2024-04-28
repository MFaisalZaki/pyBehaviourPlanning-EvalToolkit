from unified_planning.shortcuts import OneshotPlanner
from unified_planning.io import PDDLReader
import up_symk
# from fbi.shortcuts import *

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'external-pkgs', 'pyForbidBehaviourIterative'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'external-pkgs', 'pyForbidBehaviourIterative', 'fbi'))

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'external-pkgs', 'pyBehaviourSortsSuite'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'external-pkgs', 'pyBehaviourSortsSuite', 'bss'))
from fbi.shortcuts import ForbidBehaviourIterative

from .utilities import experiment_reader, getkeyvalue, read_planner_cfg, update_fbi_parameters

def solve(args):
#     # I guess the best way to do so is by using the UPWrapper.
#     # But note that now we don't have a unified wrapper since the the fbi one returns
#     # a list of two stuff. So this one will be a little bit messy.

    expdetails = experiment_reader(args.experiment_file)
    try:
        domain = getkeyvalue(expdetails, 'domainfile')
        problem = getkeyvalue(expdetails, 'problemfile')
        assert domain is not None and problem is not None, "Domain or problem file is not provided."
        task = PDDLReader().parse_problem(domain, problem)

        planner_params = read_planner_cfg(args.experiment_file)

        match expdetails['planner']:
            case 'fbi':
                # Update the behaviour space with the resources file if exists.
                planner_params = update_fbi_parameters(planner_params, expdetails)

                fbi = ForbidBehaviourIterative(task, planner_params['bspace-cfg'], planner_params['base-planner-cfg'])
                fbi.plan(getkeyvalue(expdetails, 'k'))



                with OneshotPlanner(name='FBIPlanner',  params=planner_params) as planner:
                    result = planner.solve(task)
                pass
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

    pass


