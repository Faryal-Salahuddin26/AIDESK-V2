# Git Safety & Deployment Workflow

This document describes the automated Git safety workflow for AIDesk.

## 🚀 Quick Start

### Windows (PowerShell)
```powershell
.\scripts\git-safety.ps1
```

### Linux/macOS (Bash)
```bash
bash scripts/git-safety.sh
```

## 📋 What the Scripts Do

### 1. `git-safety.sh` / `git-safety.ps1`

**Automated Security Validation**

This script performs 4 critical checks:

1. **Validates .gitignore**
   - Checks for all required patterns (.env files, storage JSON, etc.)
   - Ensures comprehensive coverage

2. **Checks Tracked Files**
   - Scans for tracked .env files
   - Scans for tracked storage JSON files
   - Scans for tracked secret files

3. **Removes Tracked Sensitive Files**
   - Automatically runs `git rm --cached` on sensitive files
   - Files remain locally but are removed from Git tracking

4. **Scans Git History**
   - Checks for secrets in commit history
   - Detects OpenAI API keys, long alphanumeric strings, database URLs

**Output**:
- ✅ **Green**: Safe to push
- ⚠️ **Yellow**: Issues found, review required
- ❌ **Red**: Critical issues, must fix before pushing

### 2. `cleanup-history.sh`

**Git History Cleanup**

Removes secrets from entire Git history using `git-filter-repo`.

**⚠️ WARNING**: 
- Rewrites Git history
- Requires force push
- Team members must re-clone repository
- **Must rotate all exposed secrets**

## 🔄 Workflow Integration

### Pre-Push Hook (Recommended)

Create `.git/hooks/pre-push`:

**Windows**:
```powershell
# .git/hooks/pre-push
powershell -ExecutionPolicy Bypass -File scripts\git-safety.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }
```

**Linux/macOS**:
```bash
#!/bin/bash
bash scripts/git-safety.sh
```

Make executable:
```bash
chmod +x .git/hooks/pre-push
```

### CI/CD Integration

Add to `.github/workflows/security-check.yml`:

```yaml
name: Git Safety Check

on: [push, pull_request]

jobs:
  security-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Git Safety Check
        run: bash scripts/git-safety.sh
```

## 📝 Usage Examples

### Before Every Push

```bash
# Run safety check
bash scripts/git-safety.sh

# If safe, proceed with push
git add .
git commit -m "Your commit message"
git push origin main
```

### If Secrets Found in History

```bash
# 1. Run cleanup script
bash scripts/cleanup-history.sh

# 2. Force push (WARNING: Rewrites history)
git push origin --force --all
git push origin --force --tags

# 3. Notify team to re-clone

# 4. ROTATE ALL EXPOSED SECRETS
# - Generate new OpenAI API keys
# - Generate new database passwords
# - Update all environment variables
```

## 🔍 What Gets Checked

### Environment Files
- ✅ `.env`
- ✅ `.env.local`
- ✅ `.env.production`
- ✅ `backend/.env`
- ✅ `frontend/.env.local`
- ✅ Any `.env*` files

### Storage Files
- ✅ `storage/news.json`
- ✅ `storage/news-data/*.json`
- ✅ `backend/storage/news.json`
- ✅ `backend/storage/news-data/*.json`

### Secret Patterns Detected
- ✅ OpenAI API keys (`sk-` prefix + 32+ chars)
- ✅ Long alphanumeric strings (40+ chars)
- ✅ Database URLs with credentials
- ✅ AWS keys
- ✅ OAuth secrets
- ✅ Generic API keys

## 🛠️ Troubleshooting

### "git-filter-repo not found"

Install it:
```bash
pip install git-filter-repo
# OR
brew install git-filter-repo  # macOS
```

### "Permission denied" (Linux/macOS)

```bash
chmod +x scripts/*.sh
```

### Script fails on Windows

Use PowerShell version:
```powershell
.\scripts\git-safety.ps1
```

### Git history check is slow

The history scan can take time on large repositories. This is normal.

## ⚠️ Important Security Notes

1. **Removing from tracking ≠ Removing from history**
   - `git rm --cached` only removes from future commits
   - Use `cleanup-history.sh` to remove from history

2. **Always rotate exposed secrets**
   - If secrets were in Git history, they're compromised
   - Generate new API keys immediately
   - Update all environment variables

3. **Coordinate force pushes**
   - History cleanup requires force push
   - Notify team before force pushing
   - Team must re-clone after force push

4. **Never commit .env files**
   - Always use `.env.example` as template
   - Add actual values to `.env` (which is gitignored)

## 📊 Script Output Examples

### Safe Repository
```
========================================
AIDesk Git Safety & Deployment Workflow
========================================

[1/4] Validating .gitignore...
✅ .gitignore contains all required patterns

[2/4] Checking for tracked sensitive files...
✅ No sensitive files are tracked

[3/4] Removing tracked sensitive files from Git...
✅ No files need to be removed

[4/4] Checking Git history for secrets...
✅ No secrets found in Git history

========================================
Summary
========================================
✅ Repository is SAFE to push!
```

### Issues Found
```
[2/4] Checking for tracked sensitive files...
❌ Found tracked .env files:
   - backend/.env
   - frontend/.env.local

[3/4] Removing tracked sensitive files from Git...
   ✓ Removed: backend/.env
   ✓ Removed: frontend/.env.local
✅ Files removed from Git tracking (still exist locally)

⚠️  Issues found. Please review above.
Files have been removed from tracking. Commit these changes:
  git add .gitignore
  git commit -m 'Security: Remove sensitive files from tracking'
```

## 🎯 Best Practices

1. **Run before every push**: `bash scripts/git-safety.sh`
2. **Use pre-push hooks**: Automate the check
3. **Never commit secrets**: Always use environment variables
4. **Review .gitignore regularly**: Ensure coverage
5. **Rotate exposed secrets**: If found in history, generate new ones
6. **Coordinate history cleanup**: Notify team before force push

## 📚 Additional Resources

- [Git Filter Repo Documentation](https://github.com/newren/git-filter-repo)
- [Git Security Best Practices](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

