# Testing Guide - Verify Data Fetching

## 🧪 Quick Test Steps

### 1. Start Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 2. Test Backend Endpoints

#### Test List Endpoint (should return empty array)
```bash
curl http://localhost:8000/list-news
```

**Expected Response:**
```json
{
  "articles": [],
  "count": 0,
  "total": 0
}
```

#### Test Pipeline Endpoint (collects articles)
```bash
curl -X POST http://localhost:8000/run-full-pipeline \
  -H "Content-Type: application/json" \
  -d "{\"topic\": \"AI news latest\", \"max_articles\": 5}"
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Pipeline completed. Processed X articles, saved Y.",
  "count": X,
  "saved": Y,
  "errors": []
}
```

#### Test List Endpoint Again (should return articles)
```bash
curl http://localhost:8000/list-news
```

**Expected Response:**
```json
{
  "articles": [
    {
      "title": "...",
      "slug": "...",
      "url": "...",
      ...
    }
  ],
  "count": X,
  "total": X
}
```

### 3. Start Frontend Server
```bash
cd frontend
npm run dev
```

### 4. Test Frontend

1. Open browser: http://localhost:3000
2. Open DevTools (F12) → Console tab
3. Check for any errors
4. Check Network tab → Look for `/list-news` request
5. Verify response status is 200

---

## 🔍 Debugging Checklist

### Backend Issues

#### Issue: Backend won't start
**Check:**
- [ ] Python dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file exists with `OPENAI_API_KEY`
- [ ] Port 8000 is not in use

#### Issue: Pipeline returns 0 articles
**Check:**
- [ ] OpenAI API key is valid
- [ ] Internet connection working
- [ ] Check backend logs for errors

#### Issue: Articles not saving
**Check:**
- [ ] `backend/storage/` directory exists
- [ ] `backend/storage/news.json` is writable
- [ ] Check backend logs for save errors

### Frontend Issues

#### Issue: "No Articles Available" message
**Check:**
- [ ] Backend is running
- [ ] `NEXT_PUBLIC_API_URL` is set correctly
- [ ] Network request succeeds (check DevTools)
- [ ] Storage file has articles

#### Issue: CORS errors
**Check:**
- [ ] Backend CORS allows `http://localhost:3000`
- [ ] Backend is running

#### Issue: API returns 500
**Check:**
- [ ] Backend logs show error
- [ ] Storage file exists and is readable
- [ ] Database file exists (for auth)

---

## 📊 Expected Data Flow

```
1. User visits homepage
   ↓
2. Frontend calls GET /list-news
   ↓
3. Backend reads storage/news.json
   ↓
4. Backend returns articles array
   ↓
5. Frontend displays articles
```

---

## ✅ Success Criteria

- [ ] Backend starts without errors
- [ ] `GET /list-news` returns valid JSON
- [ ] Pipeline collects articles successfully
- [ ] Articles are saved to storage/news.json
- [ ] Frontend displays articles on homepage
- [ ] No console errors in browser
- [ ] No CORS errors

---

## 🚨 Common Error Messages

### "No Articles Available"
**Meaning:** Storage file is empty
**Fix:** Run collection pipeline

### "Failed to fetch"
**Meaning:** Backend not running or CORS issue
**Fix:** Start backend, check CORS settings

### "500 Internal Server Error"
**Meaning:** Backend error
**Fix:** Check backend logs

### "CORS policy blocked"
**Meaning:** CORS not configured
**Fix:** Check backend CORS middleware

