# AIDesk Frontend

Next.js 14 frontend for AIDesk AI-powered news platform.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

### 3. Start Development Server

```bash
npm run dev
```

Visit `http://localhost:3000`

## 🔌 Backend Connection

The frontend connects to the backend API at:
- Development: `http://localhost:8000`
- Production: Set via `NEXT_PUBLIC_API_URL` environment variable

### Backend Endpoints Used

- `GET /api/v1/list-news` - List all articles
- `GET /api/v1/news/{slug}` - Get article by slug

## 📝 Notes

- Make sure the backend is running before starting the frontend
- If backend is not available, the frontend will show "No articles yet"
- Backend should be running on port 8000 by default

## 🛠️ Troubleshooting

### Frontend won't start

1. **Check if dependencies are installed:**
   ```bash
   npm install
   ```

2. **Check for TypeScript errors:**
   ```bash
   npm run build
   ```

3. **Check if port 3000 is available:**
   - Change port: `npm run dev -- -p 3001`

### Can't connect to backend

1. **Verify backend is running:**
   ```bash
   curl http://localhost:8000/api/v1/list-news
   ```

2. **Check environment variables:**
   - Ensure `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`

3. **Check CORS settings:**
   - Backend must allow `http://localhost:3000` in CORS_ORIGINS

### No articles showing

1. **Backend might not have articles yet:**
   - Generate articles via backend API
   - Or wait for scheduled task to run

2. **Check browser console for errors**

3. **Verify API endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/list-news
   ```

