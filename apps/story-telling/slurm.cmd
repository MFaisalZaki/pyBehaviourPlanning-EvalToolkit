#!/bin/bash
#SBATCH --job-name=app-story
#SBATCH --partition=sturm-part
#SBATCH -e /data/ma342/app-storyline/apps/story-telling/slurm/app-story.error
#SBATCH -o /data/ma342/app-storyline/apps/story-telling/slurm/app-story.output
#SBATCH --cpus-per-task=1
#SBATCH --mem=16GB
#SBATCH --time=01:00:00

source /data/ma342/app-storyline/v-env/bin/activate && cd /data/ma342/app-storyline/apps/story-telling && python3 main.py && deactivate
