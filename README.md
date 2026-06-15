# AI Research Assistant

A full-stack Retrieval-Augmented Generation (RAG) application that lets you upload PDF documents and ask natural-language questions about them. Answers are grounded in the actual document content, with page-level source citations so you can verify exactly where each answer came from.

**Live Demo:** [ai-research-assistant-lac.vercel.app](https://ai-research-assistant-lac.vercel.app)
**Backend API:** [ai-research-assistant-08j9.onrender.com/docs](https://ai-research-assistant-08j9.onrender.com/docs)

> Note: the backend runs on Render's free tier, which spins down after periods of inactivity. The first request after inactivity may take 30-60 seconds while the server wakes up.

---

## Features

- 📄 Upload one or more PDF documents
- 💬 Ask questions in natural language about uploaded content
- 🔍 Answers are retrieved via semantic search and grounded in source text — no hallucinated answers from outside the documents
- 📑 View the exact source excerpts (with page numbers and relevance scores) used to generate each answer
- 🗂️ Multi-document support — chat across all uploaded PDFs simultaneously
- ☁️ Fully deployed: frontend on Vercel, backend on Render

---

## How It Works

```
┌──────────────┐         ┌───────────────────┐         ┌──────────────────┐
│   Next.js     │  HTTP   │     FastAPI        │         │   Google Gemini   │
│   Frontend    │ ◄─────► │     Backend        │ ◄─────► │   (Embeddings +   │
│  (Vercel)     │         │   (Render)         │         │   Generation)     │
└──────────────┘         │                    │         └──────────────────┘
                          │  ┌──────────────┐  │
                          │  │  ChromaDB     │  │
                          │  │ (Vector Store)│  │
                          │  └──────────────┘  │
                          └────────────────────┘
```

**Ingest pipeline (on upload):**
1. PDF text is extracted page-by-page (`pypdf`)
2. Text is split into overlapping chunks (`langchain-text-splitters`)
3. Each chunk is embedded using Gemini's `gemini-embedding-001` model
4. Chunks + embeddings + metadata (document ID, page number) are stored in ChromaDB

**Query pipeline (on chat):**
1. The user's question is embedded (using a query-optimized embedding mode)
2. ChromaDB performs a semantic similarity search to retrieve the most relevant chunks
3. Retrieved chunks are passed as context to Gemini 2.5 Flash, with a system prompt constraining it to answer only from the provided context
4. The answer and source chunks (with page numbers and relevance scores) are returned to the frontend

---

## Tech Stack

**Frontend**
- Next.js 15 (App Router) + TypeScript
- Tailwind CSS + shadcn/ui (Radix primitives)
- Deployed on Vercel

**Backend**
- FastAPI (Python)
- Pydantic for request/response validation
- Deployed on Render

**AI / RAG**
- Google Gemini 2.5 Flash (generation)
- Gemini Embedding (`gemini-embedding-001`)
- LangChain (`RecursiveCharacterTextSplitter` for chunking)
- ChromaDB (persistent vector store)

**Resilience**
- `tenacity` for retry-with-exponential-backoff on transient Gemini API errors

---

## Project Structure

```
ai-research-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, router registration
│   │   ├── routes/               # API endpoints (/upload, /chat)
│   │   ├── services/             # Business logic (parsing, chunking, embedding,
│   │   │                          #   vector store, retrieval, generation, RAG pipeline)
│   │   ├── core/                  # Configuration (env vars)
│   │   └── models/                 # Pydantic schemas
│   ├── requirements.txt
│   └── render.yaml
│
└── frontend/
    ├── app/                       # Next.js App Router pages
    ├── components/                # UI components (uploader, chat, message bubbles)
    └── lib/
        ├── api/                   # API client functions
        └── types/                 # Shared TypeScript types
```

---

## API Endpoints

| Method | Endpoint  | Description |
|--------|-----------|-------------|
| `GET`  | `/`       | Health check |
| `POST` | `/upload` | Upload a PDF; runs the full ingest pipeline (parse → chunk → embed → store) |
| `POST` | `/chat`   | Ask a question; runs the RAG query pipeline and returns an answer with source chunks |

Full interactive API documentation is available at `/docs` (Swagger UI).

---

## Running Locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create a .env file with your Gemini API key:
echo "GEMINI_API_KEY=your_key_here" > .env

uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000` (docs at `/docs`).

### Frontend

```bash
cd frontend
npm install

# Create .env.local pointing to your local backend:
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > .env.local

npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## Known Limitations

- **Ephemeral storage**: Render's free tier filesystem is wiped on redeploy/restart — uploaded PDFs and the ChromaDB vector store do not persist long-term. A production version would use S3 (or similar) for file storage and a managed/persistent vector database.
- **Synchronous ingestion**: PDF processing (chunking + embedding) happens synchronously within the `/upload` request, so larger documents take longer to upload. A production version would offload this to a background job queue.
- **Gemini free-tier rate limits**: the demo uses a free-tier API key with daily request quotas. If you see rate-limit errors, it's likely the daily quota has been reached rather than an application bug.

---

## What I Learned

This project was built as a structured, end-to-end deep dive into RAG systems — covering embeddings, semantic search, vector databases, chunking strategy, prompt engineering for grounded generation, full-stack integration, and deployment of independently-hosted frontend/backend services with cross-origin configuration.
