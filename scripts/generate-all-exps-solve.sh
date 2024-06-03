

python3.11 exp-runner/initenv.py

mkdir -p sandbox-classical-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/all-exps/classical-behaviour-count/exp-fbi-behaviour-count     $(pwd)/sandbox-classical-behaviour-count-exp/fbi
./scripts/generate-solve-exp.sh $(pwd)/all-exps/classical-behaviour-count/exp-fi-behaviour-count      $(pwd)/sandbox-classical-behaviour-count-exp/fi
./scripts/generate-solve-exp.sh $(pwd)/all-exps/classical-behaviour-count/exp-symk-behaviour-count    $(pwd)/sandbox-classical-behaviour-count-exp/symk

./scripts/generate-solve-exp.sh $(pwd)/all-exps/exp-fbi-different-encodings $(pwd)/sandbox-fbi-different-encodings

mkdir -p sandbox-numeric-behaviour-count-exp
./scripts/generate-solve-exp.sh $(pwd)/all-exps/numeric-behaviour-count/exp-fbi-behaviour-count $(pwd)/sandbox-numeric-behaviour-count-exp/sandbox-fbi-behaviour-count