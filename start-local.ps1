Write-Host 'Starting local James Law dashboard...' -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1
uvicorn app:app --reload
