Write-Host 'Setting up local Python environment...' -ForegroundColor Cyan

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ''
Write-Host 'Local setup complete.' -ForegroundColor Green
Write-Host 'Run this to start locally:' -ForegroundColor Cyan
Write-Host 'uvicorn app:app --reload'
