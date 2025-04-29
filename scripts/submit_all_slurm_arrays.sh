#!/bin/bash

# Usage: ./submit_all_slurm_arrays.sh /path/to/split_jobs

PARENT_DIR="$1"

if [[ -z "$PARENT_DIR" ]]; then
    echo "Usage: $0 /path/to/split_jobs"
    exit 1
fi

SLURM_SCRIPTS_DIR="$PARENT_DIR/slurm-scripts"

if [[ ! -d "$SLURM_SCRIPTS_DIR" ]]; then
    echo "Error: Slurm scripts directory '$SLURM_SCRIPTS_DIR' does not exist."
    exit 2
fi

for slurm_script in "$SLURM_SCRIPTS_DIR"/submit_dir_*.slurm; do
    # Extract dir name (e.g., dir_1, dir_2)
    DIR_NAME=$(basename "$slurm_script" | sed 's/submit_\(dir_[0-9]\+\)\.slurm/\1/')

    TASK_DIR="$PARENT_DIR/$DIR_NAME"

    if [[ ! -d "$TASK_DIR" ]]; then
        echo "Warning: Task directory '$TASK_DIR' not found for script '$slurm_script'. Skipping."
        continue
    fi

    # Count the number of .txt files in the directory
    NUM_TASKS=$(ls "$TASK_DIR"/*.txt 2>/dev/null | wc -l)

    if [[ "$NUM_TASKS" -eq 0 ]]; then
        echo "Warning: No .txt files in '$TASK_DIR'. Skipping."
        continue
    fi

    echo "Submitting: $slurm_script with array size 1-$NUM_TASKS"

    # Submit the job
    sbatch -p bigmem --array=1-"$NUM_TASKS" "$slurm_script"
done

echo "All submissions done."