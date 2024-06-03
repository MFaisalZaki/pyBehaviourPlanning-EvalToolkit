

python3.11 exp-runner/initenv.py

mkdir -p sandbox-classical-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/all-exps/classical-behaviour-count/fbi        $(pwd)/sandbox-classical-behaviour-count-exp/fbi
./scripts/generate-solve-exp.sh $(pwd)/all-exps/classical-behaviour-count/fi-bspace  $(pwd)/sandbox-classical-behaviour-count-exp/fi-bspace
./scripts/generate-solve-exp.sh $(pwd)/all-exps/classical-behaviour-count/fi-maxsum  $(pwd)/sandbox-classical-behaviour-count-exp/fi-maxsum
./scripts/generate-solve-exp.sh $(pwd)/all-exps/classical-behaviour-count/fi-first-k $(pwd)/sandbox-classical-behaviour-count-exp/fi-first-k
./scripts/generate-solve-exp.sh $(pwd)/all-exps/classical-behaviour-count/symk       $(pwd)/sandbox-classical-behaviour-count-exp/symk

./scripts/generate-solve-exp.sh $(pwd)/all-exps/different-encodings/fbi $(pwd)/sandbox-fbi-different-encodings

mkdir -p sandbox-numeric-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/all-exps/numeric-behaviour-count/exp-fbi-behaviour-count $(pwd)/sandbox-numeric-behaviour-count-exp/sandbox-fbi-behaviour-count