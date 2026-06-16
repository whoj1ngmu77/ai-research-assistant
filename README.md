# AI Research Assistant

A full-stack RAG (Retrieval-Augmented Generation) application where users can upload PDF documents and ask natural language questions, receiving answers grounded in their documents with source citations — now with authentication, persistent chat history, streaming responses, and usage analytics.

**[Live Demo](https://ai-research-assistant-ean8jjj6i.vercel.app)** · **[Backend API](https://ai-research-assistant-08j9.onrender.com/docs)**

---

## Features

### Core RAG
- Upload multiple PDF documents
- Ask natural language questions across uploaded documents
- Answers grounded in source documents with page-level citations
- Collapsible source panel with relevance percentages
- Multi-document semantic search
- Authentication — Google OAuth via NextAuth (Auth.js v5), JWT-based cross-service auth, per-user data isolation in ChromaDB
- Session Memory — persistent chat history with SQLite, sidebar listing previous conversations, resume any past session
- Streaming Responses — token-by-token answer streaming via Server-Sent Events, answers appear live as Gemini generates them
- Usage Analytics — real-time dashboard showing documents uploaded, questions asked, average response time, and total chunks stored

---

## Architecture

```
┌─────────────────────────────┐         ┌──────────────────────────────────┐
│   Next.js Frontend          │  HTTPS  │   FastAPI Backend                │
│   (Vercel)                  │ ◄─────► │   (Render)                       │
│                             │  JWT    │                                  │
│ - Google OAuth (NextAuth)   │         │ - /upload  (auth required)       │
│ - Chat sidebar              │         │ - /chat    (auth required)       │
│ - Streaming UI              │         │ - /chat/stream (SSE streaming)   │
│ - Analytics dashboard       │         │ - /sessions  (CRUD)              │
│ - Source citations          │         │ - /analytics                     │
└─────────────────────────────┘         │                                  │
                                        │ - PDF parsing (pypdf)            │
                                        │ - Chunking (LangChain)           │
                                        │ - Embeddings (Gemini)            │
                                        │ - Vector search (ChromaDB)       │
                                        │ - Generation (Gemini 2.5 Flash)  │
                                        │ - Sessions DB (SQLite)           │
                                        └──────────────────────────────────┘
```

---

## Tech Stack

### Frontend
- **Next.js 15** (App Router, TypeScript, Turbopack)
- **Tailwind CSS** + **shadcn/ui** (Radix primitives, Nova preset)
- **NextAuth (Auth.js v5)** — Google OAuth, JWT session management
- **lucide-react** — icons

### Backend
- **FastAPI** (Python) — REST API + SSE streaming endpoint
- **SQLAlchemy** + **SQLite** — chat session and message persistence
- **ChromaDB** — persistent vector database with per-user metadata filtering
- **LangChain** — RecursiveCharacterTextSplitter for document chunking
- **tenacity** — retry with exponential backoff for Gemini API resilience

### AI
- **Gemini 2.5 Flash** — answer generation (streaming + non-streaming)
- **gemini-embedding-001** — 3072-dimensional semantic embeddings
  - RETRIEVAL_DOCUMENT task type for stored chunks
  - RETRIEVAL_QUERY task type for user questions

### Deployment
- **Vercel** — frontend (auto-deploy from GitHub)
- **Render** — backend (auto-deploy from GitHub, free tier)

---

## RAG Pipeline

```
Upload:
PDF file → pypdf (per-page text extraction)
        → RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
        → gemini-embedding-001 (RETRIEVAL_DOCUMENT, 3072-dim vectors)
        → ChromaDB (stored with user_id, document_id, page_number metadata)

Query:
User question → gemini-embedding-001 (RETRIEVAL_QUERY)
             → ChromaDB similarity search (top-4, filtered by user_id)
             → Gemini 2.5 Flash (grounded generation with system prompt)
             → Streamed token-by-token to frontend via SSE
             → Saved to SQLite (full answer + sources)
```

---

## Local Development

### Prerequisites
- Python 3.13+
- Node.js 18+
- Gemini API key ([get one here](https://aistudio.google.com/app/apikey))
- Google OAuth credentials ([Google Cloud Console](https://console.cloud.google.com/))

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key
AUTH_SECRET=your_auth_secret_here
```

```bash
uvicorn app.main:app --reload
# API running at http://127.0.0.1:8000
# Interactive docs at http://127.0.0.1:8000/docs
```

### Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
AUTH_SECRET=your_auth_secret_here
AUTH_GOOGLE_ID=your_google_client_id
AUTH_GOOGLE_SECRET=your_google_client_secret
```

```bash
npm run dev
# App running at http://localhost:3000
```

---

## Project Structure

```
ai-research-assistant/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── auth.py              # JWT verification dependency
│   │   │   ├── config.py            # Environment variable loading
│   │   │   └── database.py          # SQLAlchemy engine + session factory
│   │   ├── models/
│   │   │   ├── db_models.py         # ChatSession, Message, UsageEvent ORM
│   │   │   └── schemas.py           # Pydantic request/response schemas
│   │   ├── routes/
│   │   │   ├── upload.py            # POST /upload
│   │   │   ├── chat.py              # POST /chat, POST /chat/stream
│   │   │   ├── sessions.py          # GET/POST/DELETE /sessions
│   │   │   └── analytics.py         # GET /analytics
│   │   ├── services/
│   │   │   ├── pdf_parser.py        # pypdf text extraction
│   │   │   ├── chunker.py           # LangChain text splitting
│   │   │   ├── embedder.py          # Gemini embedding generation
│   │   │   ├── vector_store.py      # ChromaDB (per-user filtered)
│   │   │   ├── generator.py         # Gemini generation + stream_answer()
│   │   │   ├── ingest.py            # Upload pipeline orchestration
│   │   │   ├── rag_pipeline.py      # Query pipeline orchestration
│   │   │   ├── session_service.py   # Chat session/message CRUD
│   │   │   └── analytics_service.py # Event logging + aggregation
│   │   └── main.py                  # FastAPI app, CORS, routers
│   ├── requirements.txt
│   └── render.yaml
│
└── frontend/
    ├── app/
    │   ├── api/auth/[...nextauth]/route.ts
    │   ├── layout.tsx
    │   └── page.tsx
    ├── components/
    │   ├── AuthButton.tsx       # Sign in/out with Google
    │   ├── Providers.tsx        # SessionProvider wrapper
    │   ├── Sidebar.tsx          # Chat session list
    │   ├── ChatInterface.tsx    # Streaming chat UI
    │   ├── MessageBubble.tsx    # Message with collapsible sources
    │   ├── PdfUploader.tsx      # File upload component
    │   └── AnalyticsPanel.tsx   # Usage stats dashboard
    ├── lib/
    │   ├── api/
    │   │   ├── chat.ts          # sendChatMessage + streamChatMessage
    │   │   ├── upload.ts        # uploadPdf
    │   │   ├── sessions.ts      # Session API calls
    │   │   └── analytics.ts     # getAnalytics
    │   └── types/index.ts
    └── auth.ts                  # NextAuth config with custom JWT callback
```

---

## Key Engineering Decisions

**Why mint a custom HS256 JWT instead of using NextAuth's session cookie?**
NextAuth's session is stored as JWE (JSON Web Encryption). Decrypting it in Python requires replicating NextAuth's internal key derivation, which is version-dependent and fragile. A simple HS256 token signed with the shared AUTH_SECRET is a stable, well-documented contract between frontend and backend.

**Why per-user ChromaDB filtering instead of separate collections?**
A single collection with user_id metadata and $eq where-filtering scales better than one collection per user — avoids collection proliferation and keeps the ChromaDB client simple.

**Why save the user message to DB before calling Gemini?**
If Gemini fails (rate limit, transient 5xx), the user's question is still preserved in their chat history — accurately reflecting "I asked this but didn't get an answer."

**Why fetch + ReadableStream instead of EventSource for streaming?**
The browser's native EventSource API only supports GET requests with no custom headers — can't send a Bearer token. fetch with ReadableStream supports POST + custom headers, giving us both authentication and streaming.

**Why RETRIEVAL_DOCUMENT vs RETRIEVAL_QUERY task types?**
Google's embedding model is task-aware — using asymmetric task types for stored chunks vs. user queries improves retrieval accuracy. Documents and questions have different linguistic shapes.

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /upload | Yes | Upload and ingest a PDF |
| POST | /chat | Yes | Ask a question (full response) |
| POST | /chat/stream | Yes | Ask a question (SSE streaming) |
| GET | /sessions | Yes | List user's chat sessions |
| POST | /sessions | Yes | Create a new session |
| GET | /sessions/{id}/messages | Yes | Get messages for a session |
| DELETE | /sessions/{id} | Yes | Delete a session |
| GET | /analytics | Yes | Get usage stats |
| GET | / | No | Health check |

---

## Known Limitations

- **Ephemeral storage on Render free tier** — ChromaDB and SQLite reset on redeploy. Production would use a managed vector DB (Pinecone, pgvector) and managed Postgres.
- **Gemini free tier** — 20 generate_content requests/day. Rate limit errors surface the exact retry delay from Google's API.
- **Scanned PDFs** — pypdf extracts text from text-based PDFs only. Scanned/image PDFs require OCR (not currently implemented).

---

## Resume Bullets

- Built a full-stack RAG application with Google OAuth, per-user ChromaDB scoping, and real-time token streaming via Server-Sent Events, deployed on Vercel + Render
- Designed a RAG pipeline using LangChain chunking, Gemini embeddings with asymmetric RETRIEVAL_DOCUMENT/QUERY task types, and ChromaDB with metadata-filtered multi-tenant retrieval
- Implemented cross-service JWT authentication (NextAuth frontend to FastAPI backend) using a custom HS256 token to avoid version-dependent JWE decryption
- Built persistent chat session management with SQLAlchemy + SQLite including auto-titled history, message persistence with JSON-serialized sources, and a collapsible sidebar
- Added usage analytics with SQLAlchemy aggregate queries (COUNT, AVG, SUM) and a live dashboard tracking documents, questions, response times, and chunk counts
