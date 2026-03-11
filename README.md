# 🤖 ADK Summarizer Agent — Cloud Run

An **AI-powered text summarization agent** built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and **Gemini 2.0 Flash**, deployed as a serverless container on **Google Cloud Run**.

> **Track Focus:** Design, build, and deploy production-ready AI agents using Gemini and ADK — moving from prototype to scalable, serverless agents on Cloud Run.

---

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [What It Does](#-what-it-does)
- [Prerequisites](#-prerequisites)
- [Local Setup](#-local-setup)
- [API Endpoints](#-api-endpoints)
- [Deploy to Cloud Run](#-deploy-to-cloud-run)
- [Test the Deployed Agent](#-test-the-deployed-agent)
- [Cleanup](#-cleanup)
- [What I Learned](#-what-i-learned)
- [Future Scope](#-future-scope)

---

## 🏗 Architecture

```
┌──────────────┐     HTTP POST      ┌─────────────────┐     ADK Runner     ┌────────────────┐
│              │  ── /summarize ──▶  │                 │  ── run_async ──▶  │                │
│   Client     │                    │  FastAPI (main)  │                    │  ADK Agent     │
│  (curl/app)  │  ◀── JSON ──────  │                 │  ◀── events ─────  │  (Gemini 2.0)  │
│              │                    │                 │                    │                │
└──────────────┘                    └─────────────────┘                    └───────┬────────┘
                                                                                  │
                                                                          uses tool│
                                                                                  ▼
                                                                        ┌──────────────────┐
                                                                        │  summarize_tool  │
                                                                        │  (extractive)    │
                                                                        └──────────────────┘
```

**Flow:**
1. Client sends a `POST /summarize` request with `{"text": "..."}`.
2. FastAPI receives the request and passes the text to the ADK Runner.
3. The Runner invokes the **Gemini 2.0 Flash** model via the ADK Agent.
4. Gemini decides to call `summarize_tool` to extract a summary.
5. The tool result is returned through the Runner → FastAPI → Client.

---

## 📁 Project Structure

```
adk-gemini-cloudrun-agent/
├── app/
│   ├── __init__.py        # Makes app/ a Python package
│   ├── agent.py           # ADK Agent, Runner, and session logic
│   ├── main.py            # FastAPI application with endpoints
│   └── tools.py           # summarize_tool — used by the agent
├── .env.example           # Template for required env variables
├── .gitignore
├── Dockerfile             # Container config for Cloud Run
├── README.md
└── requirements.txt       # Direct dependencies only
```

---

## 🔍 What It Does

This agent performs **text summarization** — one of the problem statement options:

| Input | Output |
|-------|--------|
| A long paragraph or article text | A concise summary extracted from the text |

The agent uses **Gemini 2.0 Flash** for inference and the `summarize_tool` (a custom Python function registered as an ADK tool) to produce the summary. The LLM decides *when* and *how* to call the tool based on the tool's docstring.

---

## ✅ Prerequisites

| Requirement | Why |
|-------------|-----|
| **Python 3.10+** | Runtime |
| **Google API Key** | To call the Gemini model — get one at [AI Studio](https://aistudio.google.com/apikey) |
| **Docker** (optional) | To build & test the container locally |
| **gcloud CLI** (for deploy) | To deploy to Cloud Run |

---

## 🚀 Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/ritesh-2124/adk-gemini-cloudrun-agent.git
cd adk-gemini-cloudrun-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your API key

```bash
cp .env.example .env
# Edit .env and paste your real GOOGLE_API_KEY
```

### 5. Run the server

```bash
uvicorn app.main:app --reload --port 8080
```

The server will be live at `http://localhost:8080`.

---

## 📡 API Endpoints

### `GET /` — Home / Health

```bash
curl http://localhost:8080/
```

```json
{"message": "ADK Summarizer Agent is running", "status": "healthy"}
```

### `GET /health` — Health Check

```bash
curl http://localhost:8080/health
```

```json
{"status": "ok"}
```

### `POST /summarize` — Summarize Text

```bash
curl -X POST http://localhost:8080/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Artificial intelligence is transforming how we build software. Modern AI agents can understand natural language, use tools, and make decisions autonomously. Google ADK provides a framework for building such agents with Gemini models, allowing developers to create production-ready AI systems that can be deployed as serverless containers on Cloud Run."
  }'
```

```json
{
  "summary": "Artificial intelligence is transforming how we build software..."
}
```

### Error Handling

| Status Code | When |
|-------------|------|
| `200` | Successful summarization |
| `400` | Empty text provided |
| `500` | Agent/model error |

---

## ☁️ Deploy to Cloud Run

### 1. Set up Google Cloud

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 2. Build and deploy

```bash
gcloud run deploy adk-summarizer-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_API_KEY=your-api-key-here" \
  --port 8080
```

This will:
- Build the Docker image using Cloud Build
- Push it to Artifact Registry
- Deploy to Cloud Run with HTTPS endpoint

### 3. Get the service URL

```bash
gcloud run services describe adk-summarizer-agent \
  --region us-central1 \
  --format="value(status.url)"
```

---

## 🧪 Test the Deployed Agent

```bash
SERVICE_URL=$(gcloud run services describe adk-summarizer-agent \
  --region us-central1 --format="value(status.url)")

curl -X POST "$SERVICE_URL/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Google ADK is an open-source framework for building AI agents."}'
```

---

## 🧹 Cleanup

To avoid incurring future costs, delete the Cloud Run service:

```bash
gcloud run services delete adk-summarizer-agent --region us-central1
```

---

## 📚 What I Learned

1. **ADK Project Structure** — How to organize a Python project (`__init__.py`, agent module, tools module, FastAPI entry point) for ADK deployment.
2. **Tool-Using Agents** — How to implement a custom tool with proper docstrings so Gemini knows when/how to call it.
3. **`instruction` vs `description`** — `instruction` tells the agent *how to behave*; `description` tells *other agents* what this agent can do (for multi-agent delegation).
4. **Async Runner** — Using `runner.run_async()` with `async for` to properly handle the event stream.
5. **Cloud Run Deployment** — Building a Dockerfile, configuring port 8080, and deploying with `gcloud run deploy`.
6. **IAM & Authentication** — Understanding `--allow-unauthenticated` vs service-to-service auth with IAM roles.

---

## 🔮 Future Scope

Here are ideas to make this agent more powerful in future iterations:

### Short-Term Improvements
| Improvement | Description |
|-------------|-------------|
| **Use Gemini for summarization** | Replace the extractive `summarize_tool` with a tool that calls Gemini itself for abstractive summarization |
| **Add input length limits** | Validate max text length to prevent abuse and token overflow |
| **Streaming responses** | Use SSE (Server-Sent Events) to stream the summary as it's generated |
| **Persistent sessions** | Replace `InMemorySessionService` with a database-backed session service (e.g., Firestore) |
| **API key auth** | Add API key or OAuth2 authentication to the endpoints |

### Medium-Term Extensions
| Extension | Description |
|-----------|-------------|
| **Multi-tool agent** | Add more tools: classification, sentiment analysis, keyword extraction |
| **Multi-agent system** | Create a router agent that delegates to specialized sub-agents |
| **A2A Protocol** | Expose the agent via the Agent-to-Agent (A2A) protocol with an Agent Card |
| **Cloud Logging** | Integrate with Google Cloud Logging + Cloud Trace for observability |
| **CI/CD Pipeline** | Set up Cloud Build triggers for automatic deployment on git push |

### Long-Term Vision
| Vision | Description |
|--------|-------------|
| **RAG Agent** | Add Retrieval-Augmented Generation using Vertex AI Search or a vector database |
| **Multi-modal** | Accept images/PDFs and summarize their content |
| **Frontend UI** | Build a web UI (React/Next.js) to interact with the agent |
| **Rate limiting** | Add rate limiting with Cloud Armor or API Gateway |
| **Cost optimization** | Use Cloud Run min-instances=0 and concurrency tuning for cost efficiency |

---

## 📝 License

This project is built as part of the GenAI Track Focus on ADK + Gemini + Cloud Run.

---

**Built with ❤️ using Google ADK, Gemini 2.0 Flash, FastAPI, and Cloud Run**
