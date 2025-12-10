#!/bin/bash
# Setup script for AIDesk project

echo "🚀 Setting up AIDesk project..."

# Backend setup
echo "📦 Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
echo "✅ Backend setup complete"
cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend
npm install
cp .env.example .env.local
echo "✅ Frontend setup complete"
cd ..

# Create storage directories
echo "📁 Creating storage directories..."
mkdir -p storage/news-data
touch storage/news-data/.gitkeep
echo "✅ Storage directories created"

echo "✨ Setup complete! Don't forget to:"
echo "1. Add your OPENAI_API_KEY to backend/.env"
echo "2. Configure NEXT_PUBLIC_API_URL in frontend/.env.local"
echo "3. Run 'npm run dev' in frontend/ to start development server"
echo "4. Run 'uvicorn app.main:app --reload' in backend/ to start API server"

