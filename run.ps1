$venvPath = ".\.venv"
if (Test-Path "$venvPath") {
    . "$venvPath\Scripts\Activate.ps1"
    python main.py
} else {
    Write-Host "Virtual environment not found. Run setup.ps1 first."
}