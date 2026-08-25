# 📧 AI Email Reply Agent (RAG + Multi-LLM Fallback)

An automated, intelligent email reply assistant built for educational platforms. The application leverages Retrieval-Augmented Generation (RAG) to answer incoming student/user inquiries using course knowledge bases stored in Supabase, featuring an automatic failover mechanism from Google Gemini to OpenAI.

---

## 🌟 Key Features

* **RAG-Powered Knowledge Retrieval:** Uses local vector embeddings (`all-MiniLM-L6-v2`) and Supabase Vector Search (`pgvector`) to fetch accurate course context for queries.
* **Resilient Multi-LLM Fallback:** Tries **Google Gemini** as the primary response model. Automatically falls back to **OpenAI (`gpt-4o-mini`)** if rate limits (HTTP 429) or API downtime occur.
* **Human-in-the-Loop Review:** Drafts are saved to Supabase for human review before sending.
* **Email Delivery Integration:** Sends approved replies via **Resend API** with built-in sandbox rerouting for safe testing.
* **Full-Stack Architecture:** Powered by a FastAPI backend deployed on Railway and a React frontend hosted on Vercel.

---

## 🏗 System Architecture
[ Incoming Inquiry ]
│
▼
[ FastAPI Backend ]
│
├──► Generate Query Embedding (SentenceTransformers)
├──► Perform Vector Match RPC on Supabase (pgvector)
│
▼
[ LLM Orchestrator ]
├──► Try Primary: Google Gemini
└──► If Error/Rate Limit ──► Fallback: OpenAI (gpt-4o-mini)
│
▼
[ Save Draft to Supabase ] ──► [ Review Draft in Vercel UI ]

---

## 🛠 Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, Pydantic
* **AI & Machine Learning:** Google Generative AI SDK, OpenAI API, `sentence-transformers`
* **Database & Vector Store:** Supabase (`pgvector`, PostgreSQL)
* **Email Delivery:** Resend API
* **Frontend:** React, TailwindCSS
* **Deployment:** Railway (Backend), Vercel (Frontend)

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+ installed
* Node.js & npm (for frontend)
* Supabase account with `pgvector` enabled
* API Keys for Google AI Studio, OpenAI, and Resend

---

### Environment Configuration

Create a `.env` file in the root directory:

```env
# Database
SUPABASE_URL="[https://your-supabase-project.supabase.co](https://your-supabase-project.supabase.co)"
SUPABASE_KEY="your-supabase-anon-or-service-key"

# AI Model Keys
GEMINI_API_KEY="your-gemini-api-key"
OPENAI_API_KEY="sk-proj-your-openai-api-key"

# Security & Email
API_SECRET_KEY="your-custom-backend-api-key"
RESEND_API_KEY="re_your_resend_api_key"
```

│
▼
[ Approve & Send via Resend ]
