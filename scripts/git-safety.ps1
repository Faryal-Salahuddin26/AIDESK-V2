# ============================================
# AIDesk Git Safety & Deployment Workflow (PowerShell)
# ============================================
# This script automates Git security checks and cleanup
# Run this before every push to ensure no secrets are committed

$ErrorActionPreference = "Stop"

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AIDesk Git Safety & Deployment Workflow" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# Step 1: Validate .gitignore
# ============================================
Write-Host "[1/4] Validating .gitignore..." -ForegroundColor Yellow

$GitignoreFile = ".gitignore"
$RequiredPatterns = @(
    ".env",
    ".env.local",
    ".env.production",
    "*.env",
    "**/.env",
    "backend/.env",
    "frontend/.env.local",
    "storage/news.json",
    "storage/news-data/*.json",
    "backend/storage/news.json",
    "node_modules/",
    ".next/",
    "__pycache__/",
    ".vercel"
)

$MissingPatterns = @()

if (-not (Test-Path $GitignoreFile)) {
    Write-Host "ERROR: .gitignore file not found!" -ForegroundColor Red
    exit 1
}

$GitignoreContent = Get-Content $GitignoreFile -Raw

foreach ($pattern in $RequiredPatterns) {
    $escapedPattern = [regex]::Escape($pattern)
    if ($GitignoreContent -notmatch $escapedPattern) {
        # Check if covered by more general pattern
        if ($pattern -like "*.env*" -and ($GitignoreContent -match "\.env|^\*\*/\*\.env")) {
            continue
        }
        $MissingPatterns += $pattern
    }
}

if ($MissingPatterns.Count -eq 0) {
    Write-Host ".gitignore contains all required patterns" -ForegroundColor Green
} else {
    Write-Host "WARNING: Missing patterns in .gitignore:" -ForegroundColor Red
    foreach ($pattern in $MissingPatterns) {
        Write-Host "   - $pattern"
    }
}

Write-Host ""

# ============================================
# Step 2: Check for tracked sensitive files
# ============================================
Write-Host "[2/4] Checking for tracked sensitive files..." -ForegroundColor Yellow

$TrackedFiles = git ls-files
$TrackedEnvFiles = $TrackedFiles | Select-String -Pattern "\.env$|\.env\.|\.envlocal"
$TrackedStorage = $TrackedFiles | Select-String -Pattern "storage/.*\.json$|backend/storage/.*\.json$"
$TrackedSecrets = $TrackedFiles | Select-String -Pattern ".*secret.*|.*password.*|.*key.*\.(pem|key|cert|crt)$"

$IssuesFound = 0

if ($TrackedEnvFiles) {
    Write-Host "Found tracked .env files:" -ForegroundColor Red
    $TrackedEnvFiles | ForEach-Object { Write-Host "   - $_" }
    $IssuesFound = 1
}

if ($TrackedStorage) {
    Write-Host "Found tracked storage JSON files:" -ForegroundColor Red
    $TrackedStorage | ForEach-Object { Write-Host "   - $_" }
    $IssuesFound = 1
}

if ($TrackedSecrets) {
    Write-Host "Found tracked secret files:" -ForegroundColor Red
    $TrackedSecrets | ForEach-Object { Write-Host "   - $_" }
    $IssuesFound = 1
}

if ($IssuesFound -eq 0) {
    Write-Host "No sensitive files are tracked" -ForegroundColor Green
} else {
    Write-Host "Sensitive files found in Git tracking" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Step 3: Remove tracked sensitive files
# ============================================
Write-Host "[3/4] Removing tracked sensitive files from Git..." -ForegroundColor Yellow

$FilesToRemove = @()

if ($TrackedEnvFiles) {
    $FilesToRemove += $TrackedEnvFiles
}

if ($TrackedStorage) {
    $FilesToRemove += $TrackedStorage
}

if ($TrackedSecrets) {
    $FilesToRemove += $TrackedSecrets
}

if ($FilesToRemove.Count -gt 0) {
    Write-Host "Removing $($FilesToRemove.Count) file(s) from Git tracking..." -ForegroundColor Yellow
    foreach ($file in $FilesToRemove) {
        $file = $file.ToString().Trim()
        if ($file -and (git ls-files --error-unmatch $file 2>$null)) {
            git rm --cached $file 2>$null
            Write-Host "   Removed: $file" -ForegroundColor Green
        }
    }
    Write-Host "Files removed from Git tracking (still exist locally)" -ForegroundColor Green
} else {
    Write-Host "No files need to be removed" -ForegroundColor Green
}

Write-Host ""

# ============================================
# Step 4: Check Git history for secrets
# ============================================
Write-Host "[4/4] Checking Git history for secrets..." -ForegroundColor Yellow

$SecretsInHistory = 0

# Check for OpenAI API keys
$gitLog = git log --all --source --full-history -p 2>$null
if ($gitLog | Select-String -Pattern "sk-[a-zA-Z0-9]{32,}") {
    Write-Host "Found potential OpenAI API keys in Git history" -ForegroundColor Red
    $SecretsInHistory = 1
}

# Check for long alphanumeric strings
if ($gitLog | Select-String -Pattern "=[a-zA-Z0-9]{40,}") {
    Write-Host "Found potential API keys (long alphanumeric strings) in Git history" -ForegroundColor Red
    $SecretsInHistory = 1
}

# Check for DATABASE_URL with credentials
if ($gitLog | Select-String -Pattern "DATABASE_URL=.*://.*:.*@") {
    Write-Host "Found potential DATABASE_URL with credentials in Git history" -ForegroundColor Red
    $SecretsInHistory = 1
}

if ($SecretsInHistory -eq 0) {
    Write-Host "No secrets found in Git history" -ForegroundColor Green
} else {
    Write-Host "Secrets detected in Git history" -ForegroundColor Yellow
    Write-Host "   Consider running: scripts\cleanup-history.sh" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# Final Summary
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($IssuesFound -eq 0 -and $SecretsInHistory -eq 0) {
    Write-Host "Repository is SAFE to push!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Review changes: git status"
    Write-Host "  2. Commit changes: git add .gitignore && git commit -m 'Security: Update .gitignore'"
    if ($FilesToRemove.Count -gt 0) {
        Write-Host "  3. Commit removals: git commit -m 'Security: Remove sensitive files from tracking'"
    }
    Write-Host "  4. Push: git push origin main"
    exit 0
} else {
    Write-Host "Issues found. Please review above." -ForegroundColor Yellow
    Write-Host ""
    if ($IssuesFound -gt 0) {
        Write-Host "Files have been removed from tracking. Commit these changes:"
        Write-Host "  git add .gitignore"
        Write-Host "  git commit -m 'Security: Remove sensitive files from tracking'"
    }
    if ($SecretsInHistory -eq 1) {
        Write-Host ""
        Write-Host "IMPORTANT: Secrets found in Git history" -ForegroundColor Red
        Write-Host "  Run: bash scripts/cleanup-history.sh"
        Write-Host "  This will rewrite Git history to remove secrets."
        Write-Host "  WARNING: This requires force push and coordination with team!"
    }
    exit 1
}

