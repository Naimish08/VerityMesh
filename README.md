# VerityMesh

**Autonomous Multi-Agent Research & Fact-Verification Platform**

VerityMesh goes beyond simple AI-generated answers. It decomposes complex research questions, dispatches specialized agents, retrieves evidence from multiple sources, extracts and verifies atomic claims, detects contradictions, and synthesizes evidence-backed reports with source-level citations.

## The Difference

| Traditional AI | VerityMesh |
|---------------|------------|
| Query → Retrieve → Generate | Research → Evidence → Verification → Challenge → Resolution → Synthesis |
| Trust the model's output | Every claim linked to source evidence |
| Single-pass generation | Multi-agent pipeline with iterative refinement |
| No provenance | Full citation chain with confidence scores |

## Architecture

```
QUESTION
   ↓
PLANNER (decompose into sub-questions)
   ↓
WEB RESEARCH AGENT (search, fetch, chunk, embed)
   ↓
EVIDENCE STORE (PostgreSQL + pgvector)
   ↓
SYNTHESIZER (cited report generation)
   ↓
EVIDENCE-BACKED REPORT
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, React, TypeScript, Tailwind CSS |
| **Backend** | Python, FastAPI, Pydantic v2 |
| **Agents** | LangGraph, Google Gemini 2.0 Flash |
| **Embeddings** | Google text-embedding-004 (768 dims) |
| **Search** | Tavily Search API |
| **Database** | PostgreSQL 17 + pgvector (HNSW) |
| **Cache/Queue** | Redis 7 |
| **Infrastructure** | Docker Compose |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Google AI Studio API key ([get one](https://aistudio.google.com/app/apikey))
- Tavily API key ([get one](https://tavily.com))

### 1. Clone & Configure

```bash
git clone <repo-url>
cd veritymesh
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Everything

```bash
docker compose up
```

This starts:
- **Frontend** → http://localhost:3000
- **Backend API** → http://localhost:8000
- **PostgreSQL** → localhost:5432
- **Redis** → localhost:6379

### 3. Use It

1. Open http://localhost:3000
2. Click "Start New Research"
3. Enter a research question (e.g., "Should Kafka or RabbitMQ be used for high-throughput order processing?")
4. Watch the live research pipeline execute
5. Read the evidence-backed report with expandable citations

## Local Development (without Docker)

### Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Start PostgreSQL and Redis separately, then:
alembic upgrade head
uvicorn main:app --reload --port 8000
```

### Worker

```bash
cd apps/api
python -m workers.research_worker
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/research` | Start a new research run |
| `GET` | `/api/research/{id}` | Get research run details |
| `GET` | `/api/research/{id}/events` | SSE stream of live progress |
| `GET` | `/api/research/{id}/claims` | List extracted claims |
| `GET` | `/api/research/{id}/sources` | List discovered sources |
| `GET` | `/api/health` | Health check |

## Project Structure

```
veritymesh/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── agents/             # LangGraph agent pipeline
│   │   │   ├── nodes/          # Agent nodes (planner, researcher, synthesizer)
│   │   │   ├── prompts/        # LLM prompt templates
│   │   │   └── tools/          # Agent tools (search, fetch)
│   │   ├── database/           # SQLAlchemy models & connection
│   │   ├── routes/             # API endpoints
│   │   ├── schemas/            # Pydantic request/response models
│   │   ├── services/           # Business logic (embeddings, retrieval)
│   │   └── workers/            # Background research worker
│   └── web/                    # Next.js frontend
│       └── src/
│           ├── app/            # Pages (App Router)
│           ├── components/     # UI components
│           ├── hooks/          # React hooks (SSE, etc.)
│           ├── stores/         # Zustand state management
│           └── types/          # TypeScript type definitions
├── database/                   # Database initialization
├── docker-compose.yml
└── .env.example
```

## Roadmap

- [x] **Phase 1 — MVP**: Question → Planner → Search → pgvector → Synthesizer → Cited Report
- [ ] **Phase 2 — Agentic**: Parallel researchers, paper agent, document upload
- [ ] **Phase 3 — Verification**: Claim extraction, verification agent, confidence scoring
- [ ] **Phase 4 — Contradictions**: Conflict detection, investigation, resolution, evidence graph
- [ ] **Phase 5 — Evaluation**: Benchmark framework, citation correctness, claim accuracy
- [ ] **Phase 6 — Production**: Auth, Redis workers, observability, LangSmith, polished UI

## License

MIT
