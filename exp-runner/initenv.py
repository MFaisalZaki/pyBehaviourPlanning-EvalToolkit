import os
import subprocess
import sys


def createVEnv(basedir, requirements_file):
    venv_dir = os.path.join(basedir, 'v-env')
    os.makedirs(venv_dir, exist_ok=True)
    ## start a venv and install the required packages.
    os.system(f'python3.10 -m venv {venv_dir}')
    os.system(f'{venv_dir}/bin/python3.10 -m pip install unified-planning z3-solver up-symk up-pyperplan networkx pytest')
    os.system(f'{venv_dir}/bin/python3.10 -m pip install git+https://github.com/MFaisalZaki/forbiditerative.git')
    os.system(f'{venv_dir}/bin/python3.10 -m pip install git+https://github.com/MFaisalZaki/pyBehaviourPlanningSMT.git')
    os.system(f'{venv_dir}/bin/python3.10 -m pip install git+https://github.com/MFaisalZaki/up-behaviour-planning.git')
    os.system(f'{venv_dir}/bin/python3.10 -m pip uninstall pypmt')
    os.system(f'{venv_dir}/bin/python3.10 -m pip install git+https://github.com/pyPMT/pyPMT.git@d44efb71746b3a91e7fb1926b4405bd14f9df33b')
    return venv_dir

def clone_and_compile_ibm_diversescore():
    IBM_DIVERSESCORE_NAME = 'ibm-diversescore'
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    IBM_DIVERSESCORE_DIR = os.path.join(CURRENT_DIR, IBM_DIVERSESCORE_NAME)
    try:
        subprocess.run(['git', 'clone', 'https://github.com/IBM/diversescore.git', IBM_DIVERSESCORE_NAME], cwd=CURRENT_DIR)
        # Apply patch
        patches = []
        patches.append(os.path.join(CURRENT_DIR, "operations", "diversescore", "patches", "diverscore.1.patch"))
        for patch in patches:
            try:
                with open(patch, 'rb') as f:
                    subprocess.check_call(['patch', '-p1'], stdin=f, cwd=CURRENT_DIR)
            except:
                pass
    except:
        pass
    subprocess.run([sys.executable, 'build.py'], cwd=IBM_DIVERSESCORE_DIR)

# This script should be run before evaluating any plans.
current_prj_dir = os.path.join(os.path.dirname(__file__), '..')
# Create a venv for to install the required packages.
venv_dir = createVEnv(current_prj_dir, os.path.join(os.path.dirname(__file__), 'operations', 'exts', 'requirements.txt'))
clone_and_compile_ibm_diversescore()