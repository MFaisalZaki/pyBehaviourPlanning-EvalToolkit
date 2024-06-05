# python3.11 exp-runner/initenv.py

mkdir -p sandbox-classical-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count/fbi        $(pwd)/sandbox-classical-behaviour-count-exp/fbi        $(pwd)/external-pkgs/classical-domains
./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count/fi-bspace  $(pwd)/sandbox-classical-behaviour-count-exp/fi-bspace  $(pwd)/external-pkgs/classical-domains
./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count/fi-maxsum  $(pwd)/sandbox-classical-behaviour-count-exp/fi-maxsum  $(pwd)/external-pkgs/classical-domains
./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count/fi-first-k $(pwd)/sandbox-classical-behaviour-count-exp/fi-first-k $(pwd)/external-pkgs/classical-domains
./scripts/generate-solve-exp.sh $(pwd)/exps/classical-behaviour-count/symk       $(pwd)/sandbox-classical-behaviour-count-exp/symk       $(pwd)/external-pkgs/classical-domains

./scripts/generate-solve-exp.sh $(pwd)/exps/different-encodings/fbi $(pwd)/sandbox-fbi-different-encodings $(pwd)/external-pkgs/classical-domains

mkdir -p sandbox-numeric-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/exps/numeric-behaviour-count/fbi $(pwd)/sandbox-numeric-behaviour-count-exp/sandbox-fbi-behaviour-count $(pwd)/external-pkgs/numeric-domains
