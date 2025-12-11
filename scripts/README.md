# Git Safety Scripts

This directory contains scripts to automate Git security checks and cleanup.

## Quick Start

### Windows (PowerShell)
```powershell
.\scripts\git-safety.ps1
```

### Linux/macOS (Bash)
```bash
bash scripts/git-safety.sh
```

## Scripts

### 1. `git-safety.sh` / `git-safety.ps1`

**Purpose**: Automated Git security validation and cleanup

**What it does**:
1. ✅ Validates `.gitignore` contains all required patterns
2. ✅ Checks for tracked sensitive files (.env, storage JSON, secrets)
3. ✅ Removes tracked sensitive files from Git (keeps local files)
4. ✅ Scans Git history for potential secrets

**Usage**:
```bash
# Run before every push
bash scripts/git-safety.sh
```

**Output**:
- ✅ Green: Safe to push
- ⚠️ Yellow: Issues found, review required
- ❌ Red: Critical issues, must fix before pushing

### 2. `cleanup-history.sh`

**Purpose**: Remove secrets from entire Git history

**⚠️ WARNING**: This rewrites Git history and requires force push!

**What it does**:
1. Creates backup branch
2. Uses `git-filter-repo` to remove secrets from all commits
3. Replaces secrets with `REMOVED_SECRET` placeholder

**Usage**:
```bash
bash scripts/cleanup-history.sh
```

**Requirements**:
- Install `git-filter-repo`:
  ```bash
  pip install git-filter-repo
  # OR
  brew install git-filter-repo  # macOS
  ```

**After running**:
1. Force push: `git push origin --force --all`
2. Notify team members to re-clone
3. **ROTATE ALL EXPOSED SECRETS** (generate new API keys)

## Workflow Integration

### Pre-Push Hook (Recommended)

Create `.git/hooks/pre-push`:
```bash
#!/bin/bash
bash scripts/git-safety.sh
```

Make it executable:
```bash
chmod +x .git/hooks/pre-push
```

### CI/CD Integration

Add to your CI pipeline:
```yaml
# .github/workflows/security-check.yml
- name: Git Safety Check
  run: bash scripts/git-safety.sh
```

## What Gets Checked

### Environment Files
- `.env`
- `.env.local`
- `.env.production`
- `backend/.env`
- `frontend/.env.local`
- Any `.env*` files

### Storage Files
- `storage/news.json`
- `storage/news-data/*.json`
- `backend/storage/news.json`
- `backend/storage/news-data/*.json`

### Secret Patterns
- OpenAI API keys (`sk-` prefix)
- Long alphanumeric strings (40+ chars)
- Database URLs with credentials
- AWS keys
- OAuth secrets

## Troubleshooting

### "git-filter-repo not found"
```bash
pip install git-filter-repo
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

## Best Practices

1. **Run before every push**: `bash scripts/git-safety.sh`
2. **Never commit .env files**: Always use `.env.example` as template
3. **Rotate exposed secrets**: If secrets were in history, generate new ones
4. **Use environment variables**: Never hardcode secrets in code
5. **Review .gitignore regularly**: Ensure all sensitive patterns are covered

## Security Notes

- ⚠️ Removing files from Git tracking doesn't remove them from history
- ⚠️ If secrets were committed, use `cleanup-history.sh` to remove them
- ⚠️ After cleaning history, **always rotate exposed secrets**
- ⚠️ Force push rewrites history - coordinate with team first

