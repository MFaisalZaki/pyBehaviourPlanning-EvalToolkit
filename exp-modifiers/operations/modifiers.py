import os 
import json
    
from .utilities import (
    getkeyvalue,
    setkeyvalue
)

def replace(args):
    for file in os.listdir(args.dir):
        if file.endswith(".json"):
            
            results_file = os.path.join(args.dir, file)
            
            with open(results_file, "r") as f:
                data = json.load(f)
            
            domainfile = getkeyvalue(data, "domainfile")
            problemfile = getkeyvalue(data, "problemfile")

            assert domainfile is not None and problemfile is not None, f"Domain or problem file not found in {results_file}."
            
            domainfile = domainfile.replace(args.tag, args.value)
            problemfile = problemfile.replace(args.tag, args.value)

            setkeyvalue(data, "domainfile", domainfile)
            setkeyvalue(data, "problemfile", problemfile)

            with open(results_file, "w") as f:
                json.dump(data, f, indent=4)
