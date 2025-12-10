# AIDesk Setup Guide

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- OpenAI API Key

## Installation Steps

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

**Important**: Install the OpenAI Agents SDK 2025:
```bash
pip install openai-agents
# OR if the package name is different:
pip install agents
```

The package must support:
- `from agents import Agent, runner`
- `from agents import functional_tool`
- `@functional_tool` decorator

### 2. Backend Environment Variables

Create `backend/.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Frontend Setup

```bash
cd aidesk
npm install
```

### 4. Frontend Environment Variables

Create `aidesk/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start Frontend (Terminal 2)
```bash
cd aidesk
npm run dev
```

Visit http://localhost:3000

## Project Structure

```
AIDesk/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main FastAPI app
│   ├── collector_agent.py  # CollectorAgent implementation
│   ├── summary_agent.py    # SummaryAgent implementation
│   ├── seo_agent.py       # SEOAgent implementation
│   └── requirements.txt   # Python dependencies
├── aidesk/                # Next.js frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   └── public/
│       └── news-data/     # JSON article storage
└── SETUP.md               # This file
```

## API Usage

### Generate Articles
```bash
curl -X POST http://localhost:8000/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI news", "max_articles": 5}'
```

### Get All Articles
```bash
curl http://localhost:8000/api/articles
```

### Get Specific Article
```bash
curl http://localhost:8000/api/articles/{slug}
```

## Troubleshooting

### Backend Issues

1. **Import Error: No module named 'agents'**
   - Install the OpenAI Agents SDK: `pip install openai-agents` or `pip install agents`
   - Verify installation: `python -c "from agents import Agent, runner"`

2. **OpenAI API Key Error**
   - Ensure `.env` file exists in `backend/` directory
   - Verify API key is set correctly

3. **Path Errors for news-data**
   - Ensure the directory structure is correct
   - The backend saves to `aidesk/public/news-data/`

### Frontend Issues

1. **Cannot connect to backend**
   - Verify backend is running on port 8000
   - Check `NEXT_PUBLIC_API_URL` in `.env.local`

2. **Build Errors**
   - Run `npm install` again
   - Clear `.next` directory: `rm -rf .next`

## Deployment

### Frontend (Vercel)
1. Connect GitHub repository
2. Set `NEXT_PUBLIC_API_URL` environment variable
3. Deploy

### Backend (Render/Fly.io)
1. Set `OPENAI_API_KEY` environment variable
2. Deploy using `render.yaml` or `fly.toml`
3. Update frontend `NEXT_PUBLIC_API_URL` to point to deployed backend

## Notes

- The OpenAI Agents SDK 2025 syntax uses `Agent`, `runner`, and `@functional_tool`
- No ChatCompletion, Swarm, or deprecated assistant API is used
- All articles are stored as JSON files (no database)
- The agents run sequentially: Collector → Summary → SEO

