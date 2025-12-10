# Deployment Guide

## Backend Deployment

### Render

1. Connect GitHub repository
2. Set environment variables:
   - `OPENAI_API_KEY`
   - `SCHEDULER_ENABLED=true`
   - `SCHEDULER_INTERVAL=600`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Fly.io

1. Install Fly CLI
2. Run: `fly launch`
3. Set secrets: `fly secrets set OPENAI_API_KEY=your_key`
4. Deploy: `fly deploy`

## Frontend Deployment

### Vercel

1. Connect GitHub repository
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-backend-url.com`
   - `NEXT_PUBLIC_SITE_URL=https://your-frontend-url.com`
3. Deploy automatically on push

## Environment Variables

### Backend
```env
OPENAI_API_KEY=your_key
DATABASE_URL=sqlite:///./aidesk.db  # Optional
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL=600
STORAGE_PATH=../storage/news-data
```

### Frontend
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_SITE_URL=https://yourdomain.com
```

