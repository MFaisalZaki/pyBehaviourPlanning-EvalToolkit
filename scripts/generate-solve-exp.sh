#!/bin/bash
# 1: exp-details-dir
# 2: sandbox-dir
# 3: planning-tasks-dir
# 4: parition. Default is sturm-part

# Check if the partition is provided
if [ -z "$4" ]
then
    PARTITION="sturm-part"
else
    PARTITION=$4
fi

# python3 exp-runner/initenv.py
source v-env/bin/activate && python $(pwd)/exp-runner/main.py generate --exp-details-dir $1 --sandbox-dir $2 --planning-tasks-dir $4 --partition $PARTITION && deactivate