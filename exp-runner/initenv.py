import os
from operations.utilities import createVEnv, install_bplanning

# This script should be run before evaluating any plans.
current_prj_dir = os.path.join(os.path.dirname(__file__), '..')
# Create a venv for to install the required packages.
venv_dir = createVEnv(current_prj_dir, os.path.join(os.path.dirname(__file__), 'operations', 'exts', 'requirements.txt'))
# Install behaviour space and forbid behaviour iterative packages.
external_packages_dir = os.path.join(os.path.dirname(__file__), '..', 'external-pkgs')
pkgs_dir = [os.path.join(external_packages_dir, pkg) for pkg in ['pyBehaviourSortsSuite', 'pyForbidBehaviourIterative']]
install_bplanning(current_prj_dir, pkgs_dir, venv_dir)