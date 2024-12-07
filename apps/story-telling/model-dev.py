import os
import unified_planning as up
from unified_planning.io import PDDLReader
from unified_planning.plans import SequentialPlan
import unified_planning.engines.results as UPResults
from unified_planning.shortcuts import PlanValidator, SequentialSimulator
from unified_planning.shortcuts import OneshotPlanner, Compiler, CompilationKind


def simulate_plan(plan, task):
    with SequentialSimulator(problem=task) as simulator:
        initial_state = simulator.get_initial_state()
        current_state = initial_state
        states = [current_state]
        for action_instance in plan.actions:
            current_state = simulator.apply(current_state, action_instance)
            if current_state is None:
                assert False, "No cost available since the plan is invalid."
            states.append(current_state)
        return states



domain  = os.path.join(os.path.dirname(__file__), 'pddl', 'mars', 'domain.pddl')
problem = os.path.join(os.path.dirname(__file__), 'pddl', 'mars', 'problem.pddl')

task = PDDLReader().parse_problem(domain, problem)

compilationlist = [
    ["up_quantifiers_remover", "QUANTIFIERS_REMOVING"],
    ["fast-downward-reachability-grounder", "GROUNDING"]
]

names = [name for name, _ in compilationlist]
compilationkinds = [kind for _, kind in compilationlist]
with Compiler(names=names, compilation_kinds=compilationkinds) as compiler:
    compiled_task = compiler.compile(task)

with OneshotPlanner(name='symk-opt',  params={"symk_search_time_limit": "900s"}) as planner:
    result   = planner.solve(compiled_task.problem)
    seedplan = result.plan if result.status in UPResults.POSITIVE_OUTCOMES else None

# states = simulate_plan(seedplan, compiled_task.problem)
# with SequentialSimulator(problem=compiled_task.problem) as simulator:
#     pass
pass

