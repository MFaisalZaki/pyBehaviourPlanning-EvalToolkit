import os
import json
from copy import deepcopy
from collections import defaultdict

import unified_planning as up
from unified_planning.shortcuts import OneshotPlanner
from unified_planning.io import PDDLReader, PDDLWriter
from behaviour_planning.over_domain_models.smt.shortcuts import GoalPredicatesOrderingSMT, MakespanOptimalCostSMT, ResourceCountSMT
from behaviour_planning.over_domain_models.smt.shortcuts import ForbidBehaviourIterativeSMT
from up_behaviour_planning.FBIPlannerUp import FBIPlanner
env = up.environment.get_environment()
env.factory.add_engine('FBIPlanner', __name__, 'FBIPlanner')

domain  = os.path.join(os.path.dirname(__file__), 'pddl', 'robin_hood', 'robin_hood_golden_arrow_domain1.pddl')
problem = os.path.join(os.path.dirname(__file__), 'pddl', 'robin_hood', 'robin_hood_golden_arrow_problem1.pddl')
resource = os.path.join(os.path.dirname(__file__), 'resources', 'robinhood_problem1_resources.txt')


domain = os.path.join(os.path.dirname(__file__), 'pddl', 'the-iliad-project', 'trunk', 'iliad-domain.pddl')
problem = os.path.join(os.path.dirname(__file__), 'pddl', 'the-iliad-project', 'trunk', 'iliad-problem-first-book.pddl')


dims  = []
dims += [(GoalPredicatesOrderingSMT, None)]
# dims += [(MakespanOptimalCostSMT, {})]
# dims += [(ResourceCountSMT, resource)]

planner_params = {
  "base-planner-cfg": {
    "planner-name": "symk-opt",
    "symk_search_time_limit": "900s",
    "k": 5
  },
  "bspace-cfg": {
    "solver-timeout-ms": 600000,
    "solver-memorylimit-mb": 16000,
    "dims": dims,
    "compliation-list": [
        ["up_quantifiers_remover", "QUANTIFIERS_REMOVING"],
        ["fast-downward-reachability-grounder", "GROUNDING"]
    ],
    "run-plan-validation": True,
    "encoder": "seq",
    "disable-after-goal-state-actions": False
  },
  "fbi-planner-type": "ForbidBehaviourIterativeSMT"
}

up.shortcuts.get_environment().error_used_name = False
task = PDDLReader().parse_problem(domain, problem)

with OneshotPlanner(name='FBIPlanner',  params=deepcopy(planner_params)) as planner:
  result = planner.solve(task)
planlist = [] if len(result[0]) <= 1 else [r.plan for r in result[0]]
planlist = list(filter(lambda p: not p is None, planlist))
logmsgs  = result[1]

results = defaultdict(dict)
results['plans'] = list(map(lambda p: p if isinstance(p, str) else f'{PDDLWriter(task).get_plan(p)}; {len(p.actions)} cost (unit)', planlist))

result_file = os.path.join(os.path.dirname(__file__), 'results', 'iliad.json')
os.makedirs(os.path.dirname(result_file), exist_ok=True)

with open(result_file, 'w') as f:
  json.dump(results, f, indent=4)

pass