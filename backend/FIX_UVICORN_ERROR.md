# Fix: "Could not import module 'app.main'" Error

## Problem
When starting uvicorn, you see:
```
ERROR: Error loading ASGI app. Could not import module "app.main".
```

## Solution

The issue is that uvicorn is trying to import `app.main` but `main.py` is in the `backend/` directory, not `backend/app/`.

### Correct Way to Start Backend

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Start uvicorn with correct module path:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   **NOT:** `uvicorn app.main:app` ❌

### Verify You're in the Right Directory

Before running uvicorn, make sure you're in the `backend/` directory:

**Windows:**
```powershell
cd E:\AIdesk\backend
uvicorn main:app --reload --port 8000
```

**Linux/macOS:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Using the Helper Scripts

**Windows:**
```powershell
.\backend\START_SERVER.bat
```

**Linux/macOS:**
```bash
bash backend/START_SERVER.sh
```

### Why This Happens

- `main.py` is located at: `backend/main.py`
- The FastAPI app is defined as `app = FastAPI(...)` in `main.py`
- So the correct import path is: `main:app`
- NOT: `app.main:app` (this would look for `backend/app/main.py`)

### Quick Check

Run this to verify:
```bash
cd backend
python -c "import main; print('✅ main.py can be imported')"
```

If this works, then `uvicorn main:app` will work too.

