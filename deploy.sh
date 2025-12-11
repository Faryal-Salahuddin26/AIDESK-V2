#!/bin/bash

# AIDesk Deployment Script
# Safely commits and pushes changes to Git
# Ensures no sensitive data is committed

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AIDesk Deployment Script ===${NC}\n"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Git repository not initialized${NC}"
    echo "Run: git init"
    exit 1
fi

# Check for sensitive files that might be staged
echo "🔍 Checking for sensitive files..."

SENSITIVE_FILES=(
    ".env"
    ".env.local"
    ".env.production"
    "backend/.env"
    "frontend/.env.local"
    "backend/aidesk.db"
    "backend/storage/news.json"
    "storage/news.json"
    "*.key"
    "*.pem"
    "*.p12"
    "*.pfx"
)

FOUND_SENSITIVE=false

for file in "${SENSITIVE_FILES[@]}"; do
    if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo -e "${RED}⚠️  WARNING: Sensitive file '$file' is tracked by Git!${NC}"
        FOUND_SENSITIVE=true
    fi
done

if [ "$FOUND_SENSITIVE" = true ]; then
    echo -e "\n${RED}❌ Aborting: Sensitive files detected in Git tracking${NC}"
    echo "Please remove them with: git rm --cached <file>"
    echo "And ensure they are in .gitignore"
    exit 1
fi

# Check for uncommitted .env files
echo "🔍 Checking for .env files..."
if find . -name ".env*" -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.next/*" | grep -q .; then
    ENV_FILES=$(find . -name ".env*" -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.next/*")
    echo -e "${YELLOW}⚠️  Found .env files (should be ignored by .gitignore):${NC}"
    echo "$ENV_FILES"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Check if there are changes to commit
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}ℹ️  No changes to commit${NC}"
    exit 0
fi

# Show what will be committed
echo -e "\n${GREEN}📋 Changes to be committed:${NC}"
git status --short

# Generate commit message
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
COMMIT_MSG="Deploy: Update project files - $TIMESTAMP"

# Check if there's a specific message from command line
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
fi

echo -e "\n${GREEN}📝 Commit message:${NC} $COMMIT_MSG"

# Confirm before proceeding
read -p "Continue with commit and push? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Stage all changes
echo -e "\n${GREEN}📦 Staging changes...${NC}"
git add .

# Double-check for sensitive files in staging
echo "🔍 Final check for sensitive files in staging..."
STAGED_FILES=$(git diff --cached --name-only)

for file in $STAGED_FILES; do
    for sensitive in "${SENSITIVE_FILES[@]}"; do
        if [[ "$file" == *"$sensitive"* ]]; then
            echo -e "${RED}❌ ERROR: Sensitive file '$file' is about to be committed!${NC}"
            echo "Unstaging and aborting..."
            git reset HEAD "$file"
            exit 1
        fi
    done
done

# Commit changes
echo -e "\n${GREEN}💾 Committing changes...${NC}"
git commit -m "$COMMIT_MSG"

# Push to remote
echo -e "\n${GREEN}🚀 Pushing to remote...${NC}"
if git push; then
    echo -e "\n${GREEN}✅ Successfully deployed!${NC}"
else
    echo -e "\n${RED}❌ Push failed. Check your Git remote configuration.${NC}"
    exit 1
fi

echo -e "\n${GREEN}✨ Deployment complete!${NC}"

