# pyBehaviourPlanningEvalToolkit
Evaluation toolkit for the Behaviour Planning Approach

# How to run.
```
parallel -j1 sbatch :::: commands.txt
```

To run the score command:
```
python exp-runner/main generate --exp-details-dir $(pwd)/exps/classical-behaviour-count --sandbox-dir $(pwd)/sandbox-classical-behaviour-count-exp --planning-tasks-dir $(pwd)/external-pkgs/classical-domains --partition sturm-part --for-score-exp --score-for-k 5 10 100 1000
```