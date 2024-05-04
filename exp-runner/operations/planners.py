from unified_planning.shortcuts import OneshotPlanner

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
    # this should be moved to a function
    domain  = getkeyvalue(expdetails, 'domainfile')
    problem = getkeyvalue(expdetails, 'problemfile')
    results = generate_summary_file(task, expdetails, 'FBIPlanner', planner_params, domain, problem, planlist, logmsgs)
    return results

def FIPlannerWrapper(args):
    pass

def SymKPlannerWrapper(args):
    pass