# Articles Display Guide

## ✅ Current Status

- **Backend:** Running and collecting articles
- **Articles Saved:** 6 articles in `backend/storage/news.json`
- **API Endpoint:** `/list-news` is working correctly
- **Frontend:** Ready to display articles

## 📊 Article Display Layout

The homepage displays articles in a CoinDesk-style layout:

1. **Featured Article** (1st article)
   - Large card with image
   - Full title and summary
   - Prominent display

2. **Medium Cards** (articles 2-4)
   - 3-column grid on desktop
   - Medium-sized cards with images
   - Title and short summary

3. **Small Cards** (articles 5-10)
   - 3-column grid on desktop
   - Compact cards
   - Title and summary

## 🔍 Troubleshooting

### Articles Not Showing?

1. **Check Backend is Running**
   ```bash
   curl http://localhost:8000/list-news
   ```
   Should return JSON with articles.

2. **Check Frontend Environment**
   ```bash
   # Verify .env.local exists
   cat frontend/.env.local
   
   # Should contain:
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Hard Refresh Browser**
   - Press `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
   - Clears cache and forces reload

4. **Check Browser Console**
   - Open DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for `/list-news` request

5. **Verify Articles Exist**
   ```bash
   cd backend
   python -c "import json; print(len(json.load(open('storage/news.json'))))"
   ```

## 🚀 Quick Test

1. **Start Backend** (if not running):
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend** (if not running):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Visit Homepage**:
   ```
   http://localhost:3000
   ```

4. **Expected Result**:
   - Should see "Latest News" section
   - Featured article displayed at top
   - Medium cards below
   - Small cards in grid

## 📝 Article Data Structure

Each article should have:
- `title` - Article title
- `slug` - URL-friendly identifier
- `short_summary` - Brief description
- `source` - Source name (e.g., "youtube", "techcrunch")
- `published_at` - ISO date string
- `thumbnail` - Image URL (optional)
- `url` - Original article URL

## 🔄 Refresh Articles

To collect more articles:
```bash
curl -X POST http://localhost:8000/run-full-pipeline \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news latest", "max_articles": 10}'
```

## ✅ Verification Checklist

- [ ] Backend server is running
- [ ] `/list-news` endpoint returns articles
- [ ] Frontend server is running
- [ ] `NEXT_PUBLIC_API_URL` is set correctly
- [ ] Browser shows articles (not empty state)
- [ ] No console errors
- [ ] Articles are clickable and link to detail pages

