# DeptAI — AI-Powered Administrative Assistant

A full-stack, domain-restricted AI assistant for academic departments using RAG (Retrieval-Augmented Generation) + local LLM (Ollama). No OpenAI, no paid APIs, fully private.

---

## 🏗 Architecture

```
User Query
    ↓
Authentication (JWT)
    ↓
Query Preprocessing
    ↓
Cache Check ← SKIP if cached (500ms vs 2500ms)
    ↓
Domain Check (keyword heuristics -> Multi-Layer)
    ↓ (in-domain only)
Structured Retrieval (FAQ + Procedures DB)  ←── SQLite
    +
RAG Retrieval [Semantic Search - FAISS] + [Keyword Search - BM25] → BLEND   ←── SentenceTransformers
    ↓
Reranking - Cross-Encoder ←  Improves accuracy 15%
    ↓
Confidence Scoring ← Smart routing
    ↓
Context Assembly + Validation ←  Catch hallucinations
    ↓
Ollama LLM Generation(llama3.2 local)
    ↓
Response Validation ← Fact-checking
    ↓
Cache Storage + Logging ← Visibility
    ↓
Response + Confidence + Sources → Frontend
```

---

## 📁 Project Structure

```
deptai/
├── backend/                    # FastAPI backend
│   ├── main.py                 # App entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py         # JWT auth (register, login, refresh)
│   │   │   ├── chat.py         # Main chat endpoint (hybrid pipeline)
│   │   │   ├── faqs.py         # FAQ CRUD
│   │   │   ├── procedures.py   # Procedure CRUD
│   │   │   ├── documents.py    # File upload + async indexing
│   │   │   └── admin.py        # Dashboard, logs, user mgmt
│   │   ├── core/
│   │   │   ├── config.py       # Pydantic settings
│   │   │   ├── database.py     # SQLAlchemy setup
│   │   │   └── security.py     # JWT + password hashing
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── faq.py
│   │   │   ├── procedure.py
│   │   │   ├── document.py
│   │   │   └── query_log.py
│   │   ├── rag/
│   │   │   ├── pipeline.py     # Orchestrator (index + retrieve)
|   |   |   ├── bm25_search.py  # Keyword Search
│   │   │   ├── extractor.py    # PDF/DOCX/TXT text extraction
│   │   │   ├── chunker.py      # Sentence-aware text chunking
|   |   |   ├── reranker.py     # Cross-Encoder
│   │   │   ├── embedder.py     # SentenceTransformers wrapper
│   │   │   └── vector_store.py # FAISS index management
│   │   └── services/
│   │       ├── domain_checker.py       # Query domain restriction
│   │       ├── structured_retrieval.py # FAQ/Procedure search
│   │       └── ollama_client.py        # Local LLM client
│   └── scripts/
│       └── seed_db.py          # Initial data seeding
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.js              # Routes
│   │   ├── context/
│   │   │   └── AuthContext.js  # Auth state + API calls
│   │   ├── utils/
│   │   │   └── api.js          # Axios client (all API calls)
│   │   ├── routes/
│   │   │   └── ProtectedRoute.js
│   │   ├── components/layout/
│   │   │   └── AdminLayout.js
│   │   └── pages/
│   │       ├── student/
│   │       │   ├── LandingPage.js
│   │       │   ├── StudentLogin.js
│   │       │   ├── StudentSignup.js
│   │       │   └── ChatPage.js      ← Real API integration
│   │       └── admin/
│   │           ├── AdminLogin.js
│   │           ├── AdminDashboard.js ← Real API integration
│   │           ├── FAQManager.js
│   │           ├── ProcedureManager.js
│   │           ├── DocumentUpload.js ← Real API integration
│   │           └── QueryLogs.js      ← Real API integration
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.ai) installed and running

### Step 1 — Install Ollama and pull a model

```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2        # Recommended (2GB)
# OR for smaller/faster:
ollama pull qwen2.5:3b      # 1.9GB
ollama pull mistral          # 4.1GB
```

### Step 2 — Backend Setup

```bash
cd backend

# Copy and configure environment
cp .env.example .env
# Edit .env: set SECRET_KEY, OLLAMA_MODEL, etc.

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed the database (creates admin user + initial FAQs)
python scripts/seed_db.py

# Start the backend
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000
API docs: http://localhost:8000/api/docs

### Step 3 — Frontend Setup

```bash
cd frontend

npm install --legacy-peer-deps

# Create .env
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env

npm start
```

Frontend will be available at: http://localhost:3000

---

## 🐳 Docker Deployment

```bash
# Copy env file
cp backend/.env.example backend/.env
# Edit SECRET_KEY in backend/.env

docker-compose up --build

# Pull the LLM model into the Ollama container
docker exec -it deptai-ollama ollama pull llama3.2

# Seed the database
docker exec -it deptai-backend python scripts/seed_db.py
```

---

## 🔐 Default Credentials

| Role  | Email          | Password   |
| ----- | -------------- | ---------- |
| Admin | admin@dept.edu | Admin@2025 |

> ⚠️ Change these immediately in production!

### Creating student accounts

Students register via `/signup` on the frontend. Or via API:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Student Name","email":"s@dept.edu","student_id":"CSE-2024-001","password":"pass123"}'
```

---

## 📖 API Reference

| Method | Endpoint                    | Auth     | Description             |
| ------ | --------------------------- | -------- | ----------------------- |
| POST   | /api/auth/register          | —        | Student registration    |
| POST   | /api/auth/login             | —        | Student login           |
| POST   | /api/auth/admin/login       | —        | Admin login             |
| POST   | /api/auth/refresh           | —        | Refresh JWT             |
| GET    | /api/auth/me                | Student+ | Current user profile    |
| POST   | /api/chat/message           | Student+ | Send chat message       |
| GET    | /api/chat/history           | Student+ | Chat history            |
| GET    | /api/faqs/                  | —        | List FAQs               |
| POST   | /api/faqs/                  | Admin    | Create FAQ              |
| PUT    | /api/faqs/{id}              | Admin    | Update FAQ              |
| DELETE | /api/faqs/{id}              | Admin    | Delete FAQ              |
| GET    | /api/procedures/            | —        | List procedures         |
| POST   | /api/procedures/            | Admin    | Create procedure        |
| GET    | /api/documents/             | Admin    | List documents          |
| POST   | /api/documents/upload       | Admin    | Upload & index document |
| POST   | /api/documents/{id}/reindex | Admin    | Re-index document       |
| DELETE | /api/documents/{id}         | Admin    | Delete document         |
| GET    | /api/admin/dashboard        | Admin    | Dashboard stats         |
| GET    | /api/admin/logs             | Admin    | Query logs              |
| GET    | /api/admin/users            | Admin    | List students           |
| GET    | /api/health                 | —        | System health check     |

---

## ⚙️ Configuration (.env)

| Variable         | Default                | Description                     |
| ---------------- | ---------------------- | ------------------------------- |
| SECRET_KEY       | (change this!)         | JWT signing key                 |
| OLLAMA_MODEL     | llama3.2               | Ollama model name               |
| OLLAMA_BASE_URL  | http://localhost:11434 | Ollama server URL               |
| EMBEDDING_MODEL  | all-MiniLM-L6-v2       | SentenceTransformers model      |
| CHUNK_SIZE       | 512                    | Tokens per chunk                |
| CHUNK_OVERLAP    | 50                     | Token overlap between chunks    |
| TOP_K_RESULTS    | 5                      | FAISS search results            |
| DOMAIN_THRESHOLD | 0.35                   | Domain check minimum score      |
| DEPARTMENT_NAME  | CSE                    | Department name for LLM context |

---

## 🧠 RAG Pipeline Details

### Indexing (on document upload)

1. **Extract** — PyPDF2 (PDF), python-docx (DOCX), or plain text
2. **Clean** — normalize whitespace, remove non-printable chars
3. **Chunk** — sentence-aware sliding window (512 tokens, 50 overlap)
4. **Embed** — `all-MiniLM-L6-v2` (384-dim, L2-normalized)
5. **Store** — FAISS FlatIP index (cosine similarity via normalized IP)
6. **Persist** — index saved to `data/faiss_index/`

### Retrieval (on chat message)

1. **Domain check** — keyword heuristics + hard-reject patterns
2. **Structured** — token-overlap scoring against FAQ/Procedure DB
3. **Semantic** — embed query → FAISS search → top-K chunks
4. **Hybrid** — merge structured + RAG context
5. **Generate** — Ollama LLM synthesizes response from context

---

## 🛡 Security Notes

- JWT access tokens expire in 60 minutes
- Refresh tokens expire in 7 days
- Passwords hashed with bcrypt (12 rounds)
- All admin endpoints require `role=admin` token
- Domain restriction rejects non-department queries
- No data sent to external APIs (fully local)

---

## 🔧 Troubleshooting

**Ollama not responding:**

```bash
ollama serve          # Start Ollama
ollama list           # Check available models
ollama pull llama3.2  # Pull model if missing
```

**FAISS index not found:**
Upload documents via Admin → Documents. Index is built automatically.

**SentenceTransformers slow on first run:**
Model downloads on first use (~90MB). Subsequent runs use cache.

**CORS errors in browser:**
Ensure `FRONTEND_URL=http://localhost:3000` in backend `.env`.

**Student ID format rejected:**
Must match pattern: `CSE-2024-001` (DEPT-YEAR-NUMBER).
