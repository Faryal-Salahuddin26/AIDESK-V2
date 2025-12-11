# How to Start the Application

## 🚀 Quick Start Guide

### Step 1: Start Backend Server

Open a terminal and run:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend:**
- Visit: http://localhost:8000/docs (FastAPI docs)
- Visit: http://localhost:8000/list-news (should return empty array)

---

### Step 2: Start Frontend Server

Open **another terminal** and run:

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 15.x.x
  - Local:        http://localhost:3000
  - Ready in X ms
```

**Verify Frontend:**
- Visit: http://localhost:3000
- Should show homepage (may show "No Articles Available" if no data)

---

### Step 3: Collect News Articles (Optional)

To populate data, run the collection pipeline:

**Option 1: Using curl**
```bash
curl -X POST http://localhost:8000/run-full-pipeline \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news latest", "max_articles": 10}'
```

**Option 2: Using PowerShell**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/run-full-pipeline" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"topic": "AI news latest", "max_articles": 10}'
```

**Option 3: Using Browser**
Visit: http://localhost:8000/docs
- Click on `/run-full-pipeline` endpoint
- Click "Try it out"
- Enter JSON: `{"topic": "AI news latest", "max_articles": 10}`
- Click "Execute"

---

## 🔍 Troubleshooting

### Backend Won't Start

**Error: "Address already in use"**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Error: "Module not found"**
```bash
cd backend
pip install -r requirements.txt
```

**Error: "OPENAI_API_KEY not found"**
- Create `backend/.env` file
- Add: `OPENAI_API_KEY=your_key_here`

---

### Frontend Won't Start

**Error: "Port 3000 already in use"**
```bash
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F
```

**Error: "Module not found"**
```bash
cd frontend
npm install
```

---

### Frontend Shows "No Articles Available"

**This is normal if:**
- Backend hasn't collected articles yet
- Storage file is empty

**To fix:**
1. Make sure backend is running
2. Run the collection pipeline (see Step 3 above)
3. Refresh the frontend page

---

### Connection Refused Error

**Error: "ERR_CONNECTION_REFUSED"**

**Causes:**
- Backend server is not running
- Wrong port number
- Firewall blocking connection

**Solution:**
1. Check if backend is running: `curl http://localhost:8000/`
2. Verify port 8000 is not blocked
3. Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`

---

## 📋 Environment Variables

### Backend (.env)
```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your-secret-key-min-32-characters
DATABASE_URL=sqlite:///./aidesk.db
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

---

## ✅ Verification Checklist

- [ ] Backend server starts without errors
- [ ] Backend responds at http://localhost:8000/docs
- [ ] Frontend server starts without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] No console errors in browser DevTools
- [ ] `/list-news` endpoint returns valid JSON
- [ ] Homepage displays (even if empty)

---

## 🎯 Next Steps

1. **Start both servers** (backend + frontend)
2. **Collect articles** using the pipeline
3. **Verify articles appear** on homepage
4. **Test article detail pages**
5. **Test category pages**

---

## 📞 Need Help?

Check these files:
- `FIXES_APPLIED.md` - All fixes applied
- `TESTING_GUIDE.md` - Testing instructions
- `PROJECT_REVIEW.md` - Full project review

