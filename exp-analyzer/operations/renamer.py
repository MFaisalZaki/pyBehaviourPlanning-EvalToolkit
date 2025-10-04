import os
import json

def readfiles(directoryfrom, directoryto):
    # list files in the directory
    instances = list()
    for file in map(lambda x: os.path.join(directoryfrom, x), os.listdir(directoryfrom)):
        if not file.endswith('.json'): continue
        with open(file, 'r') as f:
            data = json.load(f)
        if len(data) < 2: continue
        data['info']['tag'] = f"{data['info']['tag']}-naive"
        newfilename = os.path.basename(file).replace('fbi-utility-value', 'fbi-utility-value-naive')
        with open(os.path.join(directoryto, newfilename), 'w') as f:
            json.dump(data, f, indent=4)
        instances.append(data)
    return instances

from_path = '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-oversubscription-behaviour-count-exp/0.25/corrupted-score-dump-results'
to_path      = '/Users/mustafafaisal/Developer/pyBehaviourPlanning-EvalToolkit/sandbox-oversubscription-behaviour-count-exp/0.25/score-dump-results'
readfiles(from_path, to_path)