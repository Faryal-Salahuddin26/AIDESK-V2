# Deployment Guide

## 🚀 Quick Deployment

### Using PowerShell (Windows)
```powershell
.\deploy.ps1
```

### Using Bash/Linux/Mac/Git Bash
```bash
chmod +x deploy.sh
./deploy.sh
```

### With Custom Commit Message
```powershell
.\deploy.ps1 "Add new features and fix bugs"
```

```bash
./deploy.sh "Add new features and fix bugs"
```

---

## 🔒 Safety Features

The deployment scripts include multiple safety checks:

### 1. **Sensitive File Detection**
Automatically checks for and prevents committing:
- `.env` files (all variants)
- Database files (`aidesk.db`)
- Storage files (`news.json`)
- Private keys (`.key`, `.pem`, `.p12`, `.pfx`)

### 2. **Pre-Commit Validation**
- Verifies sensitive files aren't tracked by Git
- Checks for `.env` files before staging
- Double-checks staging area before commit

### 3. **User Confirmation**
- Shows what will be committed
- Requires confirmation before proceeding
- Displays commit message for review

---

## 📋 What the Script Does

1. ✅ Checks if Git is initialized
2. ✅ Scans for sensitive files
3. ✅ Shows changes to be committed
4. ✅ Generates commit message (or uses custom)
5. ✅ Stages all changes (`git add .`)
6. ✅ Final safety check before commit
7. ✅ Commits changes (`git commit`)
8. ✅ Pushes to remote (`git push`)

---

## ⚠️ Important Notes

### Before First Use

1. **Configure Git Remote** (if not already done):
   ```bash
   git remote add origin <your-repo-url>
   git branch -M main
   ```

2. **Verify .gitignore**:
   - Ensure all sensitive files are listed
   - Run: `git check-ignore -v .env` (should show .gitignore rule)

3. **Test the Script**:
   - Run with `--dry-run` or review changes first
   - Check what will be committed before pushing

---

## 🛡️ Security Checklist

Before deploying, ensure:

- [ ] `.env` files are in `.gitignore`
- [ ] `backend/.env` is ignored
- [ ] `frontend/.env.local` is ignored
- [ ] `backend/aidesk.db` is ignored
- [ ] `storage/news.json` is ignored
- [ ] No API keys in code
- [ ] No passwords in code
- [ ] No private keys in repository

---

## 🔍 Manual Verification

If you want to verify what will be committed:

```bash
# Check what's staged
git status

# See what files will be committed
git diff --cached --name-only

# Verify sensitive files are ignored
git check-ignore -v .env backend/.env frontend/.env.local
```

---

## 🐛 Troubleshooting

### Error: "Sensitive files detected"
**Solution:** Remove from Git tracking:
```bash
git rm --cached backend/.env
git rm --cached frontend/.env.local
```

### Error: "Git repository not initialized"
**Solution:** Initialize Git:
```bash
git init
```

### Error: "Push failed"
**Solution:** Check remote configuration:
```bash
git remote -v
git remote set-url origin <your-repo-url>
```

### Error: "Permission denied" (Linux/Mac)
**Solution:** Make script executable:
```bash
chmod +x deploy.sh
```

---

## 📝 Commit Message Format

Default format:
```
Deploy: Update project files - YYYY-MM-DD HH:MM:SS
```

Custom format:
```bash
./deploy.sh "Fix: Resolve image loading issues"
```

---

## ✅ Post-Deployment

After successful deployment:

1. Verify changes on GitHub/GitLab
2. Check that sensitive files are NOT in the repository
3. Test the deployed application
4. Monitor for any issues

---

## 🔄 Alternative: Manual Deployment

If you prefer manual control:

```bash
# 1. Review changes
git status

# 2. Stage changes
git add .

# 3. Commit
git commit -m "Your commit message"

# 4. Push
git push
```

---

## 📚 Related Files

- `.gitignore` - Defines ignored files
- `scripts/git-safety.sh` - Git safety validation
- `GIT_SAFETY_WORKFLOW.md` - Git security guide

