# python3.11 exp-runner/initenv.py

mkdir -p sandbox-classical-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count/fbi  $(pwd)/sandbox-classical-behaviour-count-exp/fbi  $(pwd)/external-pkgs/classical-domains
./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count/fi   $(pwd)/sandbox-classical-behaviour-count-exp/fi   $(pwd)/external-pkgs/classical-domains
./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count/symk $(pwd)/sandbox-classical-behaviour-count-exp/symk $(pwd)/external-pkgs/classical-domains

# list all slurm scripts
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-classical-behaviour-count-exp/fbi/slurm-solve-scripts  $(pwd)/sandbox-classical-behaviour-count-exp/fbi-cmds.txt
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-classical-behaviour-count-exp/fi/slurm-solve-scripts   $(pwd)/sandbox-classical-behaviour-count-exp/fi-cmds.txt
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-classical-behaviour-count-exp/symk/slurm-solve-scripts $(pwd)/sandbox-classical-behaviour-count-exp/symk-cmds.txt

mkdir -p sandbox-fbi-different-encodings-exp
./scripts/generate-solve-exp.sh $(pwd)/exps/different-encodings/fbi $(pwd)/sandbox-fbi-different-encodings-exp $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-fbi-different-encodings-exp/slurm-solve-scripts $(pwd)/sandbox-fbi-different-encodings-exp/different-encodings-cmds.txt

mkdir -p sandbox-numeric-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/exps/numeric-behaviour-count/fbi $(pwd)/sandbox-numeric-behaviour-count-exp/ $(pwd)/external-pkgs/numeric-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-numeric-behaviour-count-exp/slurm-solve-scripts $(pwd)/sandbox-numeric-behaviour-count-exp/numeric-cmds.txt

mkdir -p sandbox-oversubscription-exp
./scripts/generate-solve-exp.sh $(pwd)/exps/oversubscription-diverse-planning $(pwd)/sandbox-oversubscription-behaviour-count-exp/ $(pwd)/external-pkgs/classical-domains
./scripts/collect-slurm-scripts.sh $(pwd)/sandbox-oversubscription-behaviour-count-exp/slurm-solve-scripts $(pwd)/sandbox-oversubscription-behaviour-count-exp/oversubscription-cmds.txt