python3.11 exp-runner/initenv.py

./scripts/generate-solve-exp.sh $(pwd)/exps/ppltl-classical-behaviour-count $(pwd)/sandbox-ppltl-classical-behaviour-count-exp $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-ppltl-classical-behaviour-count/slurm-solve-scripts $(pwd)/sandbox-ppltl-classical-behaviour-count/fbicmds.txt

