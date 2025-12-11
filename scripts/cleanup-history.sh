#!/bin/bash

# ============================================
# AIDesk Git History Cleanup Script
# ============================================
# This script removes secrets from entire Git history using git filter-repo
# WARNING: This rewrites Git history and requires force push!

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${RED}========================================${NC}"
echo -e "${RED}Git History Cleanup - SECRET REMOVAL${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  WARNING: This script will rewrite Git history!${NC}"
echo -e "${YELLOW}⚠️  All team members must re-clone the repository after this!${NC}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${BLUE}Aborted.${NC}"
    exit 0
fi

# Check if git-filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo -e "${YELLOW}git-filter-repo not found. Installing...${NC}"
    echo ""
    echo "Installation options:"
    echo "  1. pip install git-filter-repo"
    echo "  2. brew install git-filter-repo (macOS)"
    echo "  3. Download from: https://github.com/newren/git-filter-repo"
    echo ""
    read -p "Have you installed git-filter-repo? (yes/no): " installed
    
    if [ "$installed" != "yes" ]; then
        echo -e "${RED}Please install git-filter-repo first.${NC}"
        exit 1
    fi
    
    if ! command -v git-filter-repo &> /dev/null; then
        echo -e "${RED}git-filter-repo still not found. Please install it.${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}Creating backup branch...${NC}"
git branch backup-before-cleanup-$(date +%Y%m%d-%H%M%S) || true

echo ""
echo -e "${BLUE}Creating expressions file for git-filter-repo...${NC}"

# Create expressions file to remove secrets
EXPRESSIONS_FILE=$(mktemp)
cat > "$EXPRESSIONS_FILE" << 'EOF'
# Remove OpenAI API keys (sk- prefix followed by 32+ chars)
regex:OPENAI_API_KEY=sk-[a-zA-Z0-9]{32,}==>OPENAI_API_KEY=REMOVED_SECRET
regex:OPENAI_API_KEY\s*=\s*sk-[a-zA-Z0-9]{32,}==>OPENAI_API_KEY=REMOVED_SECRET
regex:"OPENAI_API_KEY"\s*:\s*"sk-[a-zA-Z0-9]{32,}"==>"OPENAI_API_KEY":"REMOVED_SECRET"

# Remove any long alphanumeric strings that look like API keys (40+ chars)
regex:=\s*[a-zA-Z0-9]{40,}==>=REMOVED_SECRET
regex:\s*=\s*"[a-zA-Z0-9]{40,}"==>="REMOVED_SECRET"

# Remove DATABASE_URL with credentials
regex:DATABASE_URL=.*://.*:.*@.*==>DATABASE_URL=REMOVED_SECRET
regex:DATABASE_URL\s*=\s*.*://.*:.*@.*==>DATABASE_URL=REMOVED_SECRET

# Remove other common API key patterns
regex:API_KEY\s*=\s*[a-zA-Z0-9]{32,}==>API_KEY=REMOVED_SECRET
regex:SECRET\s*=\s*[a-zA-Z0-9]{32,}==>SECRET=REMOVED_SECRET
regex:PASSWORD\s*=\s*[a-zA-Z0-9]{16,}==>PASSWORD=REMOVED_SECRET
regex:TOKEN\s*=\s*[a-zA-Z0-9]{32,}==>TOKEN=REMOVED_SECRET

# Remove AWS keys
regex:AWS_ACCESS_KEY_ID\s*=\s*[A-Z0-9]{20,}==>AWS_ACCESS_KEY_ID=REMOVED_SECRET
regex:AWS_SECRET_ACCESS_KEY\s*=\s*[a-zA-Z0-9/+=]{40,}==>AWS_SECRET_ACCESS_KEY=REMOVED_SECRET

# Remove Google OAuth secrets
regex:GOOGLE_CLIENT_SECRET\s*=\s*[a-zA-Z0-9_-]{24,}==>GOOGLE_CLIENT_SECRET=REMOVED_SECRET
regex:NEXTAUTH_SECRET\s*=\s*[a-zA-Z0-9]{32,}==>NEXTAUTH_SECRET=REMOVED_SECRET
EOF

echo -e "${GREEN}✅ Expressions file created${NC}"
echo ""

echo -e "${BLUE}Running git-filter-repo to clean history...${NC}"
echo -e "${YELLOW}This may take several minutes...${NC}"
echo ""

# Run git-filter-repo with the expressions file
git filter-repo \
    --replace-text "$EXPRESSIONS_FILE" \
    --force \
    --refs HEAD \
    --all

# Clean up expressions file
rm -f "$EXPRESSIONS_FILE"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}History cleanup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT NEXT STEPS:${NC}"
echo ""
echo "1. Verify the cleanup:"
echo "   git log --all --source --full-history -p | grep -i 'REMOVED_SECRET'"
echo ""
echo "2. Force push to remote (WARNING: This rewrites remote history):"
echo "   git push origin --force --all"
echo "   git push origin --force --tags"
echo ""
echo "3. Notify all team members:"
echo "   - They must delete their local repository"
echo "   - They must re-clone from remote"
echo "   - Any local branches will need to be recreated"
echo ""
echo "4. Rotate all exposed secrets:"
echo "   - Generate new OpenAI API keys"
echo "   - Generate new database passwords"
echo "   - Update all environment variables"
echo ""
echo -e "${RED}⚠️  DO NOT skip step 4 - exposed secrets must be rotated!${NC}"

