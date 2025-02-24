# Update pip
pip install --upgrade pip

# Install uv (package manager for python)
pip install uv

# Choose the script path
$venvPath = ".venv"

# Check if the virtual environment exists
if (-not (Test-Path $venvPath)) {
    # Create the virtual environment
    uv create $venvPath
}

# Install requirements.txt dependencies
uv pip install -r requirements.txt