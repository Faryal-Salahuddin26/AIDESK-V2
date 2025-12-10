# AIDesk - Complete Project Structure

```
AIDesk/
├── frontend/                          # Next.js Frontend
│   ├── app/                          # App Router
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Homepage
│   │   ├── news/
│   │   │   └── [slug]/
│   │   │       └── page.tsx         # Dynamic news page
│   │   └── api/                     # API routes (if needed)
│   ├── components/                   # React Components
│   │   ├── ui/                      # Shadcn UI components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
│   │   ├── Header.tsx               # Site header
│   │   ├── Footer.tsx               # Site footer
│   │   ├── NewsCard.tsx             # News card component
│   │   └── SummaryCard.tsx         # Summary card component
│   ├── lib/                         # Utilities
│   │   ├── utils.ts                # Helper functions
│   │   ├── api.ts                  # API client
│   │   └── articles.ts              # Article utilities
│   ├── public/                      # Static assets
│   │   ├── news-data/               # JSON fallback storage
│   │   └── ...
│   ├── styles/                      # Global styles
│   │   └── globals.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Configuration
│   │   ├── database.py              # Database connection
│   │   ├── models/                  # Database models
│   │   │   ├── __init__.py
│   │   │   └── article.py
│   │   ├── schemas/                 # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   └── article.py
│   │   ├── api/                     # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── routes.py            # Route handlers
│   │   │   └── dependencies.py
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── news_service.py
│   │   │   └── storage_service.py
│   │   └── tasks/                   # Scheduled tasks
│   │       ├── __init__.py
│   │       └── scheduler.py
│   ├── agents/                      # AI Agents integration
│   │   ├── __init__.py
│   │   ├── collector_agent.py
│   │   ├── summary_agent.py
│   │   └── seo_agent.py
│   ├── requirements.txt
│   ├── .env.example
│   └── alembic/                     # Database migrations (if using DB)
│
├── agents/                           # AI Agents Module
│   ├── __init__.py
│   ├── collector/
│   │   ├── __init__.py
│   │   ├── youtube_collector.py
│   │   ├── forbes_collector.py
│   │   └── web_search_collector.py
│   ├── summarizer/
│   │   ├── __init__.py
│   │   └── summarizer.py
│   ├── seo/
│   │   ├── __init__.py
│   │   └── seo_generator.py
│   └── base/
│       ├── __init__.py
│       └── agent_base.py
│
├── storage/                         # JSON Storage
│   ├── news-data/                   # JSON files
│   └── .gitkeep
│
├── scripts/                         # Utility scripts
│   ├── setup.sh                    # Setup script
│   ├── start-dev.sh               # Development start
│   └── migrate-data.py            # Data migration
│
├── docs/                           # Documentation
│   ├── API.md                     # API documentation
│   ├── DEPLOYMENT.md              # Deployment guide
│   └── ARCHITECTURE.md            # Architecture docs
│
├── tests/                          # Tests
│   ├── frontend/
│   ├── backend/
│   └── agents/
│
├── .gitignore
├── LICENSE
├── README.md
└── docker-compose.yml              # Docker setup (optional)
```

