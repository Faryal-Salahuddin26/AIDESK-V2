#!/bin/bash
# Setup script for frontend environment variables

echo "Setting up frontend environment variables..."

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "Creating .env.local file..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
EOF
    echo "✅ Created .env.local"
else
    echo "⚠️  .env.local already exists"
    echo "Current contents:"
    cat .env.local
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure backend is running: cd ../backend && uvicorn main:app --reload --port 8000"
echo "2. Restart frontend: npm run dev"
echo "3. Visit http://localhost:3000"

