#!/bin/bash
# 1: exp-details-dir
# 2: sandbox-dir
# 3: parition. Default is sturm-part

# Check if the partition is provided
if [ -z "$3" ]
then
    PARTITION="sturm-part"
else
    PARTITION=$3
fi

source v-env/bin/activate && python $(pwd)/exp-runner/main.py generate --exp-details-dir $1 --sandbox-dir $2 --planning-tasks-dir $3 --partition $PARTITION --for-score-exp --score-for-k 5 10 100 1000 && deactivate