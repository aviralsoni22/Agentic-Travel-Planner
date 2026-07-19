# Agentic AI Travel Planner 🌍✈️

**Booking.ai** turns one form (where, when, who, how much) into a complete, bookable trip: round-trip flights, a hotel, and a day-by-day itinerary that fits the budget. A **LangGraph** agent pipeline searches real flight, hotel and activity data, re-plans itself whenever a step comes back over budget, and lets the LLM make the judgment calls while Python owns every dollar of arithmetic, so the budget never drifts.

---

## 🧐 The Problem Statement

### 1. The Customer Friction

Planning a trip with real-world constraints is an exhausting, fragmented process. Users are forced to juggle multiple tabs, comparing flights, vetting hotels and researching activities while mentally calculating if everything fits their budget.

When users are forced to do this "heavy lifting" manually, two critical issues arise:

* **Missed Opportunities:** Users often miss out on high-demand accommodations ("hidden gems") and optimal flight paths simply because they cannot process the volume of data efficiently.
* **High Abandonment:** The sheer difficulty of coordinating logistics leads to **decision fatigue**, causing many users to stop planning entirely and abandon their trip.

### 2. The Business Opportunity

For Online Travel Agencies (OTAs), every minute a user spends planning on an external platform is a lost revenue opportunity. When users plan on generic AI chats and book components individually, the platform loses the chance to cross-sell and earn commissions on packages.

**Why this system wins:**

* **Increased AOV (Average Order Value):** By bundling flights, hotels, and activities into one valid "product", the system naturally encourages larger, higher-margin transactions.
* **Differentiation:** In a market of identical booking engines, offering a "concierge" experience becomes a massive competitive moat.

**The Solution:** By deploying an autonomous agent system that can deliver a complete, bookable travel package (Flights + Hotels + Activities) in under **2-3 minutes**, platforms can significantly increase conversion rates, retain customers, and capture full-lifecycle value.

---

## 🏗️ Architecture

Two units: a **React frontend** and a **FastAPI backend**. The backend runs the LangGraph pipeline in a FastAPI **BackgroundTask** (no Celery/worker process) and stores job status in **Redis**; the frontend polls for the result.

```
 ┌──────────────┐   POST /plan          ┌──────────────────────────┐
 │   Frontend   │ ─────────────────────▶│  FastAPI (app.py)        │
 │ React + Vite │   GET /plan/status/id │   • enqueues BackgroundTask
 │              │ ◀─────────────────────│   • runs LangGraph pipeline
 │              │   POST /chat          │   • writes status → Redis  │
 └──────────────┘                       └───────────┬──────────────┘
                                                     │
                        ┌────────────────────────────┼───────────────────────┐
                        ▼                             ▼                        ▼
                 ┌────────────┐              ┌────────────────┐        ┌──────────────┐
                 │   Redis    │              │  LangGraph     │        │  External    │
                 │ job status │              │  StateGraph    │──tools▶│  APIs        │
                 └────────────┘              └────────────────┘        │ RapidAPI,    │
                                                                       │ Geoapify,    │
                                                                       │ Gemini(chat) │
                                                                       └──────────────┘
```

### The LangGraph pipeline (`graph.py`)

Deterministic edges, not a manager LLM. After every research node a Python **budget checkpoint** compares real cost against the money left and decides: continue, retry, or re-plan.

```
START → allocate_budget → flight_node → hotel_node → activity_node → assemble → final_critic → END
             ▲                 │            │             │                          │
             └── re-plan ──────┴────────────┴─────────────┘◀── over budget / retry ──┘
                 (MAX_REVISIONS=2)          (PER_NODE_RETRIES=2 per node)
```

| Node | Model | Does | Source |
|---|---|---|---|
| `allocate_budget` | reasoning | Returns budget split **ratios**; `budget.py` computes exact allocations | none |
| `flight_node` | worker | Round-trip search (two one-way legs, morning-out / night-return) | Booking.com / RapidAPI |
| `hotel_node` | worker | Best-value hotel within remaining budget | Booking.com / RapidAPI + Geoapify |
| `activity_node` | worker | Iconic, interest-matched attractions with realistic costs | Geoapify + model knowledge |
| `assemble` | reasoning | Day-by-day itinerary; Python overwrites all totals | prior outputs |
| `final_critic` | reasoning | Judges coherence; can trigger a bounded re-plan | assembled plan |

Over budget → re-select cheaper (2 tries) → re-plan the whole split (2 tries) → accept best-effort with the shortfall recorded in `failures`. The caps guarantee termination.

---

## ✨ Key Features

- **Deterministic graph, not a manager agent.** Control flow is code, so no tokens are wasted on delegation and runs can't spin.
- **LLM picks ratios, Python does the math.** `budget.py` computes every allocation and total, so budget arithmetic errors are impossible.
- **Bounded budget feedback loop.** Retry the node, re-plan the split, then accept best-effort. Two caps make termination provable.
- **Provider toggle.** `LLM_PROVIDER` switches worker + reasoning tiers between **Groq** (free, default) and **OpenAI**.
- **Controlled tool loop.** Tool calls are driven manually, then a no-tools call structures the output, dodging Groq's tool-enforcement crash.
- **Non-blocking.** `/plan` returns a `task_id` instantly; the pipeline runs in a BackgroundTask and the client polls `/plan/status/{id}`.
- **API caching.** `tools/cache.py` memoizes RapidAPI / Geoapify so retries reuse fetched offers.
- **Server-side chat.** `/chat` proxies Gemini with the key on the server and an itinerary-only scope guard the browser can't bypass.

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| Agent orchestration | LangGraph (`StateGraph`) + LangChain |
| Backend | FastAPI, Uvicorn, FastAPI BackgroundTasks |
| Job status | Redis |
| LLMs | Groq (`llama-3.3-70b-versatile` / `openai/gpt-oss-120b`) or OpenAI (`gpt-4.1-mini` / `gpt-4.1`) |
| Chat | Google Gemini (`gemini-2.5-flash`), server-side |
| Frontend | React 19, Vite, TypeScript, Recharts, Lucide |
| External data | Booking.com via RapidAPI (flights + hotels), Geoapify (locations) |
| Packaging | uv, Docker, docker-compose |

---

## ⚡ Run It Locally

Everything runs through Docker Compose: Redis, the FastAPI api, and the Vite frontend.

**Prerequisites:** Docker Desktop, and API keys for Groq (free, console.groq.com), RapidAPI (Booking.com), Geoapify, and Gemini.

```bash
# 1. Clone
git clone https://github.com/aviralsoni22/Agentic-Travel-Planner.git
cd Agentic-Travel-Planner

# 2. Backend env
cp agentic_travel_planner/.env.example agentic_travel_planner/.env
#   then fill in GROQ_API_KEY, RAPIDAPI_KEY, GEOAPIFY_KEY, GEMINI_API_KEY

# 3. Start everything
docker-compose up --build
```

Open **http://localhost:3000**. The api is at `http://localhost:8000` (`/docs` for the OpenAPI UI). The frontend proxies `/api` to the api service, so no frontend keys are needed. A run takes ~2 minutes; the UI polls until the itinerary is ready.

> To run just the graph once from the CLI (no server): `docker-compose run --rm api python -m agentic_travel_planner.main`.

---

## 🔌 API

`POST /plan` — start a job → `{ "status": "queued", "task_id": "<id>" }`
`GET  /plan/status/{task_id}` — poll → `processing`, then `completed` (with `plan`) or `failed` (with `error`)
`POST /chat` — itinerary-scoped Q&A via server-side Gemini → `{ "reply": "..." }`

`/plan` body: `source, destination, start_date, end_date, num_travelers, budget, interests, group_category, currency`.

---

## ☁️ Deployment

Backend → **Render** (free web service + free Redis; pipeline runs in a BackgroundTask, no paid worker). Frontend → **HuggingFace Static Space** (static Vite build calling the Render backend via `VITE_API_BASE`). A `render.yaml` Blueprint is included. Full walkthrough: **[DEPLOY.md](DEPLOY.md)**.

---

## ⚠️ Known Limitations

- **AI-curated activities can be inaccurate** (names, prices, hours). The UI shows a disclaimer; verify before booking.
- **Groq free-tier token caps** per model; switch models or set `LLM_PROVIDER=openai` for fresh quota.
- **External API dependence** (RapidAPI, Geoapify): failures are recorded in `failures`, but partial results can occur.
- **Public endpoints are unauthenticated** — fine for a demo; add rate limiting and lock `ALLOWED_ORIGINS` for production.

---

## 📁 Project Layout

```
Agentic-Travel-Planner/
├── docker-compose.yml                  # redis + api + frontend (local)
├── render.yaml                         # Render Blueprint (web + Redis)
├── DEPLOY.md                           # deployment guide
├── agentic_travel_planner/             # backend
│   ├── Dockerfile · pyproject.toml · .env.example
│   └── src/agentic_travel_planner/
│       ├── app.py                      # FastAPI: /plan, /plan/status, /chat
│       ├── graph.py                    # LangGraph StateGraph + budget checkpoints
│       ├── budget.py                   # all money arithmetic
│       ├── llms.py · prompts.py · models.py · state.py
│       ├── main.py                     # CLI: run the graph once
│       └── tools/                      # flight / hotel / activity search + cache
└── frontend/                           # React 19 + Vite + TS
    ├── App.tsx · components/ · context/
    └── services/  api.ts · gemini.ts
```

---

## 📄 License

MIT. See [LICENSE](LICENSE).

## 👤 Built by

Aviral Soni · [GitHub](https://github.com/aviralsoni22) · [LinkedIn](https://linkedin.com/in/aviralsoni22)
