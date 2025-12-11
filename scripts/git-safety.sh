#!/bin/bash

# ============================================
# AIDesk Git Safety & Deployment Workflow
# ============================================
# This script automates Git security checks and cleanup
# Run this before every push to ensure no secrets are committed

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AIDesk Git Safety & Deployment Workflow${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ============================================
# Step 1: Validate .gitignore
# ============================================
echo -e "${YELLOW}[1/4] Validating .gitignore...${NC}"

GITIGNORE_FILE=".gitignore"
REQUIRED_PATTERNS=(
    ".env"
    ".env.local"
    ".env.production"
    "*.env"
    "**/.env"
    "backend/.env"
    "frontend/.env.local"
    "storage/news.json"
    "storage/news-data/*.json"
    "backend/storage/news.json"
    "node_modules/"
    ".next/"
    "__pycache__/"
    ".vercel"
)

MISSING_PATTERNS=()

if [ ! -f "$GITIGNORE_FILE" ]; then
    echo -e "${RED}❌ ERROR: .gitignore file not found!${NC}"
    exit 1
fi

for pattern in "${REQUIRED_PATTERNS[@]}"; do
    if ! grep -qE "^${pattern//\*/\\*}$|^${pattern//\*/\\*}" "$GITIGNORE_FILE" 2>/dev/null; then
        # Check if pattern is covered by a more general pattern
        if [[ "$pattern" == *.env* ]] && grep -qE "^\.env|^\*\*/\*\.env|^\*\*/\*\.env" "$GITIGNORE_FILE" 2>/dev/null; then
            continue
        fi
        MISSING_PATTERNS+=("$pattern")
    fi
done

if [ ${#MISSING_PATTERNS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ .gitignore contains all required patterns${NC}"
else
    echo -e "${RED}⚠️  WARNING: Missing patterns in .gitignore:${NC}"
    for pattern in "${MISSING_PATTERNS[@]}"; do
        echo -e "   - $pattern"
    done
fi

echo ""

# ============================================
# Step 2: Check for tracked sensitive files
# ============================================
echo -e "${YELLOW}[2/4] Checking for tracked sensitive files...${NC}"

TRACKED_ENV_FILES=$(git ls-files | grep -E "\.env$|\.env\.|\.envlocal" || true)
TRACKED_STORAGE=$(git ls-files | grep -E "storage/.*\.json$|backend/storage/.*\.json$" || true)
TRACKED_SECRETS=$(git ls-files | grep -E ".*secret.*|.*password.*|.*key.*\.(pem|key|cert|crt)$" || true)

ISSUES_FOUND=0

if [ -n "$TRACKED_ENV_FILES" ]; then
    echo -e "${RED}❌ Found tracked .env files:${NC}"
    echo "$TRACKED_ENV_FILES" | sed 's/^/   - /'
    ISSUES_FOUND=1
fi

if [ -n "$TRACKED_STORAGE" ]; then
    echo -e "${RED}❌ Found tracked storage JSON files:${NC}"
    echo "$TRACKED_STORAGE" | sed 's/^/   - /'
    ISSUES_FOUND=1
fi

if [ -n "$TRACKED_SECRETS" ]; then
    echo -e "${RED}❌ Found tracked secret files:${NC}"
    echo "$TRACKED_SECRETS" | sed 's/^/   - /'
    ISSUES_FOUND=1
fi

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No sensitive files are tracked${NC}"
else
    echo -e "${YELLOW}⚠️  Sensitive files found in Git tracking${NC}"
fi

echo ""

# ============================================
# Step 3: Remove tracked sensitive files
# ============================================
echo -e "${YELLOW}[3/4] Removing tracked sensitive files from Git...${NC}"

FILES_TO_REMOVE=()

if [ -n "$TRACKED_ENV_FILES" ]; then
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            FILES_TO_REMOVE+=("$file")
        fi
    done <<< "$TRACKED_ENV_FILES"
fi

if [ -n "$TRACKED_STORAGE" ]; then
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            FILES_TO_REMOVE+=("$file")
        fi
    done <<< "$TRACKED_STORAGE"
fi

if [ -n "$TRACKED_SECRETS" ]; then
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            FILES_TO_REMOVE+=("$file")
        fi
    done <<< "$TRACKED_SECRETS"
fi

if [ ${#FILES_TO_REMOVE[@]} -gt 0 ]; then
    echo -e "${YELLOW}Removing ${#FILES_TO_REMOVE[@]} file(s) from Git tracking...${NC}"
    for file in "${FILES_TO_REMOVE[@]}"; do
        if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
            git rm --cached "$file" 2>/dev/null || true
            echo -e "   ${GREEN}✓${NC} Removed: $file"
        fi
    done
    echo -e "${GREEN}✅ Files removed from Git tracking (still exist locally)${NC}"
else
    echo -e "${GREEN}✅ No files need to be removed${NC}"
fi

echo ""

# ============================================
# Step 4: Check Git history for secrets
# ============================================
echo -e "${YELLOW}[4/4] Checking Git history for secrets...${NC}"

SECRETS_IN_HISTORY=0

# Check for OpenAI API keys (sk- prefix)
if git log --all --source --full-history -p | grep -qE "sk-[a-zA-Z0-9]{32,}" 2>/dev/null; then
    echo -e "${RED}⚠️  Found potential OpenAI API keys in Git history${NC}"
    SECRETS_IN_HISTORY=1
fi

# Check for long alphanumeric strings that look like API keys
if git log --all --source --full-history -p | grep -qE "=[a-zA-Z0-9]{40,}" 2>/dev/null; then
    echo -e "${RED}⚠️  Found potential API keys (long alphanumeric strings) in Git history${NC}"
    SECRETS_IN_HISTORY=1
fi

# Check for DATABASE_URL with actual credentials
if git log --all --source --full-history -p | grep -qE "DATABASE_URL=.*://.*:.*@" 2>/dev/null; then
    echo -e "${RED}⚠️  Found potential DATABASE_URL with credentials in Git history${NC}"
    SECRETS_IN_HISTORY=1
fi

if [ $SECRETS_IN_HISTORY -eq 0 ]; then
    echo -e "${GREEN}✅ No secrets found in Git history${NC}"
else
    echo -e "${YELLOW}⚠️  Secrets detected in Git history${NC}"
    echo -e "${YELLOW}   Consider running: scripts/cleanup-history.sh${NC}"
fi

echo ""

# ============================================
# Final Summary
# ============================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $ISSUES_FOUND -eq 0 ] && [ $SECRETS_IN_HISTORY -eq 0 ]; then
    echo -e "${GREEN}✅ Repository is SAFE to push!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git status"
    echo "  2. Commit changes: git add .gitignore && git commit -m 'Security: Update .gitignore'"
    if [ ${#FILES_TO_REMOVE[@]} -gt 0 ]; then
        echo "  3. Commit removals: git commit -m 'Security: Remove sensitive files from tracking'"
    fi
    echo "  4. Push: git push origin main"
    exit 0
else
    echo -e "${YELLOW}⚠️  Issues found. Please review above.${NC}"
    echo ""
    if [ $ISSUES_FOUND -gt 0 ]; then
        echo "Files have been removed from tracking. Commit these changes:"
        echo "  git add .gitignore"
        echo "  git commit -m 'Security: Remove sensitive files from tracking'"
    fi
    if [ $SECRETS_IN_HISTORY -eq 1 ]; then
        echo ""
        echo -e "${RED}⚠️  IMPORTANT: Secrets found in Git history${NC}"
        echo "  Run: bash scripts/cleanup-history.sh"
        echo "  This will rewrite Git history to remove secrets."
        echo "  WARNING: This requires force push and coordination with team!"
    fi
    exit 1
fi

