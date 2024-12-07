import os
from unified_planning.io import PDDLReader
import unified_planning.engines.results as UPResults
from unified_planning.shortcuts import OneshotPlanner, Compiler, CompilationKind


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
    result   = planner.solve(task)
    seedplan = result.plan if result.status in UPResults.POSITIVE_OUTCOMES else None

pass