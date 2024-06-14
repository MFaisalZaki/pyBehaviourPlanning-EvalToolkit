python3.11 exp-runner/initenv.py


./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count $(pwd)/sandbox-classical-behaviour-count-exp $(pwd)/external-pkgs/classical-domains

# list all slurm scripts
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-classical-behaviour-count-exp/slurm-solve-scripts $(pwd)/sandbox-classical-behaviour-count-exp/fbi-symk-fi-cmds.txt

./scripts/generate-solve-exp.sh    $(pwd)/exps/different-encodings $(pwd)/sandbox-classical-different-encodings-exp $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-classical-different-encodings-exp/slurm-solve-scripts $(pwd)/sandbox-classical-different-encodings-exp/different-encodings-cmds.txt

./scripts/generate-solve-exp.sh    $(pwd)/exps/numeric-behaviour-count $(pwd)/sandbox-numeric-behaviour-count-exp/ $(pwd)/external-pkgs/numeric-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-numeric-behaviour-count-exp/slurm-solve-scripts $(pwd)/sandbox-numeric-behaviour-count-exp/numeric-cmds.txt

mkdir -p sandbox-oversubscription-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/exps/oversubscription-diverse-planning/0.5 $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.5 $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.5/slurm-solve-scripts $(pwd)/sandbox-oversubscription-behaviour-count-exp/oversubscription-0.5-cmds.txt

./scripts/generate-solve-exp.sh $(pwd)/exps/oversubscription-diverse-planning/0.25 $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.25 $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.25/slurm-solve-scripts $(pwd)/sandbox-oversubscription-behaviour-count-exp/oversubscription-0.25-cmds.txt

./scripts/generate-solve-exp.sh $(pwd)/exps/oversubscription-diverse-planning/0.75 $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.75 $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.75/slurm-solve-scripts $(pwd)/sandbox-oversubscription-behaviour-count-exp/oversubscription-0.75-cmds.txt