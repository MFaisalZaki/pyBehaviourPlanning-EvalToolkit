python3.11 exp-runner/initenv.py

./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count $(pwd)/sandbox-classical-behaviour-count-exp $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-classical-behaviour-count-exp/slurm-solve-scripts $(pwd)/sandbox-classical-behaviour-count-exp/fbi-symk-fi-cmds.txt

./scripts/generate-solve-exp.sh    $(pwd)/exps/numeric-behaviour-count $(pwd)/sandbox-numeric-behaviour-count-exp/ $(pwd)/external-pkgs/numeric-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-numeric-behaviour-count-exp/slurm-solve-scripts $(pwd)/sandbox-numeric-behaviour-count-exp/numeric-cmds.txt

./scripts/generate-solve-exp.sh    $(pwd)/exps/empty-bs-behaviour-count $(pwd)/sandbox-empty-bs-behaviour-count-exp/ $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-empty-bs-behaviour-count-exp/slurm-solve-scripts $(pwd)/sandbox-empty-bs-behaviour-count-exp/empty-bs-cmds.txt

./scripts/generate-solve-exp.sh $(pwd)/exps/ppltl-classical-behaviour-count $(pwd)/sandbox-ppltl-classical-behaviour-count $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-ppltl-classical-behaviour-count/slurm-solve-scripts $(pwd)/sandbox-ppltl-classical-behaviour-count/fbi-ppltl-cmds.txt

mkdir -p sandbox-oversubscription-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/exps/oversubscription-diverse-planning/0.5 $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.5 $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.5/slurm-solve-scripts $(pwd)/sandbox-oversubscription-behaviour-count-exp/oversubscription-0.5-cmds.txt

./scripts/generate-solve-exp.sh $(pwd)/exps/oversubscription-diverse-planning/0.25 $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.25 $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.25/slurm-solve-scripts $(pwd)/sandbox-oversubscription-behaviour-count-exp/oversubscription-0.25-cmds.txt

./scripts/generate-solve-exp.sh $(pwd)/exps/oversubscription-diverse-planning/0.75 $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.75 $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-oversubscription-behaviour-count-exp/0.75/slurm-solve-scripts $(pwd)/sandbox-oversubscription-behaviour-count-exp/oversubscription-0.75-cmds.txt

./scripts/generate-solve-exp.sh $(pwd)/exps/oversubscription-diverse-planning/1.0 $(pwd)/sandbox-oversubscription-behaviour-count-exp/1.0 $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-oversubscription-behaviour-count-exp/1.0/slurm-solve-scripts $(pwd)/sandbox-oversubscription-behaviour-count-exp/oversubscription-1.0-cmds.txt