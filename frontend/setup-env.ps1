# PowerShell script to setup frontend environment variables

Write-Host "Setting up frontend environment variables..." -ForegroundColor Cyan

# Create .env.local if it doesn't exist
if (-not (Test-Path .env.local)) {
    Write-Host "Creating .env.local file..." -ForegroundColor Yellow
    @"
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
"@ | Out-File -FilePath .env.local -Encoding utf8
    Write-Host "✅ Created .env.local" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env.local already exists" -ForegroundColor Yellow
    Write-Host "Current contents:" -ForegroundColor Cyan
    Get-Content .env.local
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Make sure backend is running: cd ..\backend && uvicorn main:app --reload --port 8000"
Write-Host "2. Restart frontend: npm run dev"
Write-Host "3. Visit http://localhost:3000"

