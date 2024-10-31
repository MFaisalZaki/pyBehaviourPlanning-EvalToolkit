python3.11 exp-runner/initenv.py

./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count $(pwd)/sandbox-classical-behaviour-count-exp $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-classical-behaviour-count-exp/slurm-solve-scripts $(pwd)/sandbox-classical-behaviour-count-exp/fbi-symk-fi-cmds.txt

