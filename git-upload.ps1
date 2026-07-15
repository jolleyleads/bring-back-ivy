Write-Host 'Preparing GitHub upload...' -ForegroundColor Cyan

if (!(Test-Path '.git')) {
    git init
}

git add .
git commit -m 'Initial James Law Mobile Command Center'

Write-Host ''
Write-Host 'If the GitHub repo exists, run:' -ForegroundColor Yellow
Write-Host 'git remote add origin https://github.com/jolleyleads/JamesLaw-Mobile-Command-Center.git'
Write-Host 'git branch -M main'
Write-Host 'git push -u origin main'
Write-Host ''
Write-Host 'If remote already exists, run:' -ForegroundColor Yellow
Write-Host 'git push -u origin main'
