# Troubleshooting Guide

## Backend API 404 Errors

### Issue: Frontend getting 404 from `/api/v1/list-news`

**Symptoms:**
- Frontend shows: `Backend API returned 404. Is the backend running?`
- Backend logs show: `404 Not Found` for `/api/v1/list-news`

**Solution:**

1. **Verify the route is registered:**
   ```bash
   cd backend
   python -c "from app.main import app; print([r.path for r in app.routes])"
   ```
   
   You should see `/api/v1/list-news` in the list.

2. **Check if backend is running:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test the endpoint directly:**
   ```bash
   curl http://localhost:8000/api/v1/list-news?page=1&limit=10
   ```
   
   Or visit in browser: http://localhost:8000/api/v1/list-news?page=1&limit=10

4. **Check CORS settings:**
   - Make sure `CORS_ORIGINS` in `.env` includes `http://localhost:3000`
   - Or check `backend/app/config.py` for default CORS settings

5. **Verify storage directory exists:**
   ```bash
   # The storage directory should be created automatically
   # Check if it exists:
   ls storage/news-data
   ```

6. **If no articles exist:**
   - The endpoint will return an empty list, not a 404
   - To create articles, call: `POST /api/v1/collect-news` or `POST /api/v1/process`

### Common Issues:

#### 1. Route not found (404)
- **Cause:** Router not included or wrong prefix
- **Fix:** Check `backend/app/main.py` line 42: `app.include_router(router, prefix=settings.API_V1_PREFIX, tags=["news"])`
- **Verify:** `settings.API_V1_PREFIX` should be `/api/v1`

#### 2. Empty response (200 but no articles)
- **Cause:** No articles in storage directory
- **Fix:** Generate articles first:
  ```bash
  curl -X POST http://localhost:8000/api/v1/process \
    -H "Content-Type: application/json" \
    -d '{"topic": "AI news", "max_articles": 5}'
  ```

#### 3. CORS errors
- **Cause:** Frontend origin not in CORS allow list
- **Fix:** Add to `backend/.env`:
  ```
  CORS_ORIGINS=http://localhost:3000,http://localhost:3001
  ```

#### 4. Module not found errors
- **Cause:** Dependencies not installed
- **Fix:** 
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

## Frontend Cache Warning

**Warning:** `Specified "cache: no-store" and "revalidate: 60", only one should be specified.`

**Fix:** Removed `cache: 'no-store'` from `frontend/app/page.tsx` - now only uses `revalidate: 60`.

## Testing the Full Stack

1. **Start Backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Generate Articles:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/process \
     -H "Content-Type: application/json" \
     -d '{"topic": "AI news latest", "max_articles": 10}'
   ```

4. **View Articles:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000/api/v1/list-news

