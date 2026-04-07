#!/bin/bash

# Setup script for Python virtual environment and package installation
# Usage: source setup.sh
#         setup_pyenv colorama rich

setup_pyenv() {
    local VENV_DIR=~/venvs/testenv

    # 1. Create the virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment at $VENV_DIR"
        python3 -m venv "$VENV_DIR"
    fi

    # 2. Activate the virtual environment
    source "$VENV_DIR/bin/activate"

    # 3. Check if user passed packages
    if [ $# -eq 0 ]; then
        echo "Usage: setup_pyenv <package1> [package2] ..."
        return 1
    fi

    # 4. Install all packages passed as arguments
    echo "Installing packages: $*"
    pip install "$@"

    # 5. Export current dependencies to requirements.txt
    echo "Exporting dependencies to requirements.txt"
    pip freeze > requirements.txt

    echo "Environment setup complete. Virtual env: $VENV_DIR"
}
