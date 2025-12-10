# Architecture Overview

## System Architecture

```
┌─────────────┐
│   Frontend  │  Next.js + TailwindCSS + Shadcn UI
│  (Next.js)  │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────┐
│   Backend   │  FastAPI + Python
│   (FastAPI) │
└──────┬──────┘
       │
       ├──► AI Agents
       │    ├── Collector Agent
       │    ├── Summarizer Agent
       │    └── SEO Agent
       │
       └──► Storage
            └── JSON Files (storage/news-data/)
```

## Components

### Frontend
- **Framework**: Next.js 14+ with App Router
- **Styling**: TailwindCSS + Shadcn UI
- **State**: React Hooks
- **API Client**: Fetch API

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **AI SDK**: OpenAI Agents SDK 2025
- **Storage**: JSON files (database-ready)

### AI Agents
- **Collector**: Fetches from YouTube, Forbes, web search
- **Summarizer**: Generates short and long summaries
- **SEO**: Generates metadata, slugs, tags

### Storage
- **Primary**: JSON files in `storage/news-data/`
- **Future**: Database support ready

## Data Flow

1. **Collection**: Collector Agent fetches news
2. **Processing**: Summarizer generates summaries
3. **Optimization**: SEO Agent generates metadata
4. **Storage**: Articles saved as JSON files
5. **Display**: Frontend reads JSON files

## Scheduled Tasks

- Runs every 10 minutes
- Collects latest news
- Processes and saves articles
- Updates frontend automatically

