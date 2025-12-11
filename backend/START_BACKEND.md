# How to Start the Backend Server

## The Error
If you see: `ERROR: Error loading ASGI app. Could not import module "app.main"`

This means uvicorn is trying to import `app.main` but the main.py file is in the `backend/` directory, not `backend/app/`.

## Solution

### Option 1: Run from backend directory (Recommended)
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Option 2: Run with full path
```bash
cd backend
uvicorn backend.main:app --reload --port 8000
```

### Option 3: Run main.py directly
```bash
cd backend
python main.py
```

## Verify It's Working

1. Open browser: http://localhost:8000
2. You should see: `{"message":"AIDesk API","version":"1.0.0",...}`
3. Check API docs: http://localhost:8000/docs

## Test Authentication Endpoints

### Register a user:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

## Common Issues

1. **Port 8000 already in use**: Change port with `--port 8001`
2. **Module not found**: Make sure you're in the `backend/` directory
3. **Import errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`

