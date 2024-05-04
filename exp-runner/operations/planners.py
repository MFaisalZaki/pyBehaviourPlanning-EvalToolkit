import tempfile
from collections import defaultdict

from unified_planning.engines import PlanGenerationResultStatus as ResultsStatus
from unified_planning.shortcuts import OneshotPlanner, AnytimePlanner

from .utilities import update_fbi_parameters, generate_summary_file, updatekeyvalue, getkeyvalue, read_planner_cfg

def FBIPlannerWrapper(args, task, expdetails):
    # Update the behaviour space with the resources file if exists.
    planner_params = read_planner_cfg(args.experiment_file)
    planner_params = update_fbi_parameters(planner_params, expdetails)
    with OneshotPlanner(name='FBIPlanner',  params=planner_params) as planner:
        result = planner.solve(task)
    planlist = [r.plan for r in result[0]]
    logmsgs  = result[1]
    # This is hacky by I have no time to properly fix this shit.
    updatekeyvalue(planner_params, 'dims', [[d.__name__, af] for d, af in getkeyvalue(planner_params, 'dims')])
    
    results = generate_summary_file(task, expdetails, 'fbi', planner_params, planlist, logmsgs)
    return results

def FIPlannerWrapper(args):
    pass

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