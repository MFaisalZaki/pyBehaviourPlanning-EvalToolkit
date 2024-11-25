import os

from unified_planning.io import PDDLReader
from behaviour_planning.over_domain_models.smt.shortcuts import GoalPredicatesOrderingSMT, MakespanOptimalCostSMT, ResourceCountSMT
from behaviour_planning.over_domain_models.smt.shortcuts import ForbidBehaviourIterativeSMT

domain  = os.path.join(os.path.dirname(__file__), 'pddl', 'robin_hood_golden_arrow_domain1.pddl')
problem = os.path.join(os.path.dirname(__file__), 'pddl', 'robin_hood_golden_arrow_problem1.pddl')
resource = os.path.join(os.path.dirname(__file__), 'resources', 'robinhood_problem1_resources.txt')

dims  = []
dims += [(GoalPredicatesOrderingSMT, None)]
# dims += [(MakespanOptimalCostSMT, {})]
dims += [(ResourceCountSMT, resource)]

planner_params = {
  "base-planner-cfg": {
    "planner-name": "symk-opt",
    "symk_search_time_limit": "900s"
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
  }
}

task = PDDLReader().parse_problem(domain, problem)

fbi = ForbidBehaviourIterativeSMT(task, planner_params['bspace-cfg'], planner_params['base-planner-cfg'])
plans = fbi.plan()
pass