# AIDesk Deployment Script (PowerShell)
# Safely commits and pushes changes to Git
# Ensures no sensitive data is committed

$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "=== AIDesk Deployment Script ==="
Write-Host ""

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-ColorOutput Red "❌ Error: Git repository not initialized"
    Write-Host "Run: git init"
    exit 1
}

# Check for sensitive files that might be staged
Write-Host "🔍 Checking for sensitive files..."

$sensitiveFiles = @(
    ".env",
    ".env.local",
    ".env.production",
    "backend\.env",
    "frontend\.env.local",
    "backend\aidesk.db",
    "backend\storage\news.json",
    "storage\news.json",
    "*.key",
    "*.pem",
    "*.p12",
    "*.pfx"
)

$foundSensitive = $false

foreach ($file in $sensitiveFiles) {
    $gitFiles = git ls-files $file 2>$null
    if ($gitFiles) {
        Write-ColorOutput Red "⚠️  WARNING: Sensitive file '$file' is tracked by Git!"
        $foundSensitive = $true
    }
}

if ($foundSensitive) {
    Write-Host ""
    Write-ColorOutput Red "❌ Aborting: Sensitive files detected in Git tracking"
    Write-Host "Please remove them with: git rm --cached <file>"
    Write-Host "And ensure they are in .gitignore"
    exit 1
}

# Check for uncommitted .env files
Write-Host "🔍 Checking for .env files..."
$envFiles = Get-ChildItem -Path . -Filter ".env*" -Recurse -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch "\\\.git\\" -and $_.FullName -notmatch "\\node_modules\\" -and $_.FullName -notmatch "\\.next\\" }

if ($envFiles) {
    Write-ColorOutput Yellow "⚠️  Found .env files (should be ignored by .gitignore):"
    $envFiles | ForEach-Object { Write-Host "  $($_.FullName)" }
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Aborted."
        exit 0
    }
}

# Check if there are changes to commit
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-ColorOutput Yellow "ℹ️  No changes to commit"
    exit 0
}

# Show what will be committed
Write-Host ""
Write-ColorOutput Green "📋 Changes to be committed:"
git status --short

# Generate commit message
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMsg = "Deploy: Update project files - $timestamp"

# Check if there's a specific message from command line
if ($args.Count -gt 0) {
    $commitMsg = $args[0]
}

Write-Host ""
Write-ColorOutput Green "📝 Commit message: $commitMsg"

# Confirm before proceeding
$response = Read-Host "Continue with commit and push? (y/N)"
if ($response -ne "y" -and $response -ne "Y") {
    Write-Host "Aborted."
    exit 0
}

# Stage all changes
Write-Host ""
Write-ColorOutput Green "📦 Staging changes..."
git add .

# Double-check for sensitive files in staging
Write-Host "🔍 Final check for sensitive files in staging..."
$stagedFiles = git diff --cached --name-only

foreach ($file in $stagedFiles) {
    foreach ($sensitive in $sensitiveFiles) {
        if ($file -like "*$sensitive*") {
            Write-ColorOutput Red "❌ ERROR: Sensitive file '$file' is about to be committed!"
            Write-Host "Unstaging and aborting..."
            git reset HEAD $file
            exit 1
        }
    }
}

# Commit changes
Write-Host ""
Write-ColorOutput Green "💾 Committing changes..."
git commit -m $commitMsg

# Push to remote
Write-Host ""
Write-ColorOutput Green "🚀 Pushing to remote..."
try {
    git push
    Write-Host ""
    Write-ColorOutput Green "✅ Successfully deployed!"
} catch {
    Write-Host ""
    Write-ColorOutput Red "❌ Push failed. Check your Git remote configuration."
    exit 1
}

Write-Host ""
Write-ColorOutput Green "✨ Deployment complete!"

