import os

def createVEnv(basedir, requirements_file):
    venv_dir = os.path.join(basedir, 'v-env')
    os.makedirs(venv_dir, exist_ok=True)
    ## start a venv and install the required packages.
    os.system(f'python3.10 -m venv {venv_dir}')
    os.system(f'{venv_dir}/bin/python3.10 -m pip install -r {requirements_file}')
    return venv_dir

def install_bplanning(currentdir, pkgsdir, venvdir):
    for pkg in pkgsdir:
        os.chdir(pkg)
        os.system(f'{venvdir}/bin/python3.10 -m pip install .')
    os.chdir(currentdir)

# This script should be run before evaluating any plans.
current_prj_dir = os.path.join(os.path.dirname(__file__), '..')
# Create a venv for to install the required packages.
venv_dir = createVEnv(current_prj_dir, os.path.join(os.path.dirname(__file__), 'operations', 'exts', 'requirements.txt'))
# Install behaviour space and forbid behaviour iterative packages.
external_packages_dir = os.path.join(os.path.dirname(__file__), '..', 'external-pkgs')
pkgs_dir = [os.path.join(external_packages_dir, pkg) for pkg in ['pyBehaviourPlanning']]
install_bplanning(current_prj_dir, pkgs_dir, venv_dir)