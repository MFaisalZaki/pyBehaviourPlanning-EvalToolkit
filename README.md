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



slurm single batch:
```
#!/bin/bash
#SBATCH --job-name=classical-task-first-1000
#SBATCH --output=/scratch/ma342/pyBehaviourPlanning-EvalToolkit/sandbox-classical-behaviour-count-exp/slurm-array-logs/output_%A_%a.out
#SBATCH --error=/scratch/ma342/pyBehaviourPlanning-EvalToolkit/sandbox-classical-behaviour-count-exp/slurm-array-logs/error_%A_%a.err

# Get the list of job files
JOB_FILES=($(ls /scratch/ma342/pyBehaviourPlanning-EvalToolkit/sandbox-classical-behaviour-count-exp/slurm-solve-scripts/*.txt | sort))

# Select the correct job file based on SLURM_ARRAY_TASK_ID
JOB_FILE=${JOB_FILES[$((SLURM_ARRAY_TASK_ID-1))]}

sbatch -p bigmem "$JOB_FILE"
```

script to submit jobs:
```
sbatch -p bigmem --array=1-$(ls <dir>/*.txt | wc -l) <slurm-batch0file>
```