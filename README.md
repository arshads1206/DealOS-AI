# DealOS AI

> **Enterprise Investment Intelligence Operating System.**  
> An AI-powered due diligence platform designed for financial analysts to ingest, analyze, and query complex unstructured data.

---

## 📖 Project Overview
In M&A and venture capital, analysts spend hundreds of hours reading term sheets, cap tables, and financial disclosures. **DealOS AI** automates this by providing an intelligent pipeline that extracts text from various document formats, vectorizes the content, and provides a conversational interface (Hybrid Search + RAG) to interrogate the data instantly.

## 🏗 System Architecture
DealOS AI is built on a scalable, microservice-ready architecture utilizing:
- **Backend:** Python / FastAPI
- **Database:** PostgreSQL with `pgvector`
- **Cache/Queue:** Redis
- **Object Storage:** MinIO (S3 Compatible)
- **AI/ML:** OpenAI Embeddings & LLMs

*(Insert System Architecture Diagram Here)*

## ✨ Features
- **Company Workspaces:** Isolate documents and analysis per target company.
- **Multi-Format Ingestion:** Native parsing for PDF, DOCX, PPTX, Excel, and CSV.
- **Asynchronous Processing:** Background Celery/Redis workers ensure the UI remains snappy.
- **Semantic Search:** Vector embeddings power context-aware querying across thousands of pages.
- **Enterprise Security:** JWT stateless authentication and strict domain-driven architecture.

## 📂 Folder Structure (Clean Architecture)
```text
backend/app/
├── api/                  # API routers and endpoints
├── core/                 # App configuration and security
├── models/               # SQLAlchemy DB Models
├── repositories/         # Database abstraction layer
├── schemas/              # Pydantic data validation
├── services/             # Core business logic
└── document_processing/  # File parsing and chunking logic
```

## 🚀 Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- OpenAI API Key

### 1. Environment Variables
Copy the example configuration:
```bash
cp .env.example .env
# Edit .env and insert your OPENAI_API_KEY
```

### 2. Run with Docker
The entire stack (API, DB, Redis, MinIO) can be launched via Docker Compose:
```bash
docker-compose up --build
```

### 3. Access the Platform
- **API Documentation (Swagger):** `http://localhost:8000/docs`
- **MinIO Console:** `http://localhost:9001` (Check `.env` for credentials)

## 🛠 Local Development
To run the backend locally without Docker (requires external Postgres/Redis):
```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## 🗺 Future Roadmap
- **Phase 2:** Advanced Hybrid Search (BM25 + Vector).
- **Phase 3:** LangGraph Agentic Workflows for automated financial risk extraction.
- **Phase 4:** Real-time WebSocket notifications for document processing status.

## 🤝 Contribution Guide
Please read `CONTRIBUTING.md` for details on our code of conduct, and the process for submitting pull requests. Ensure all code passes `ruff` linting and `pytest` before requesting review.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.