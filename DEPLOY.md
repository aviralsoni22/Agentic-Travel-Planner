# Deployment

Backend runs as a **free Render** web service (FastAPI + the LangGraph pipeline in a
BackgroundTask) plus a **free Render Redis** (Key Value) for job status. Frontend is a
**static Vite build** hosted on a **HuggingFace Static Space** that calls the Render backend.

```
HuggingFace Static Space (frontend)  ──HTTPS──▶  Render web service (FastAPI)
                                                        │
                                                        ▼
                                                 Render Redis (job status)
```

---

## 1. Backend → Render

The repo has a `render.yaml` Blueprint at the root. It defines the web service (built from
`agentic_travel_planner/Dockerfile`) and a free Redis instance, and wires `REDIS_URL`
automatically.

1. Push the repo to GitHub (see the root README for the repo URL).
2. In Render: **New → Blueprint**, pick this repo. Render reads `render.yaml`.
3. Set the secret env vars (marked `sync: false`) in the dashboard:

   | Variable | Value |
   |---|---|
   | `GROQ_API_KEY` | your Groq key |
   | `RAPIDAPI_KEY` | your RapidAPI (Booking.com) key |
   | `GEOAPIFY_KEY` | your Geoapify key |
   | `GEMINI_API_KEY` | your Gemini key (for chat) |
   | `ALLOWED_ORIGINS` | your HF Space origin, e.g. `https://<user>-<space>.hf.space` |

   > Deploy the frontend first if you want the exact Space URL, or set `ALLOWED_ORIGINS`
   > after the Space exists and redeploy. You can also set it to `*` temporarily to test.

4. Deploy. Note the service URL, e.g. `https://travel-planner-api.onrender.com`.
   Verify `https://<service>.onrender.com/docs` loads.

> Free-tier note: the web service spins down after ~15 min idle, so the first request
> after idle has a cold start (up to ~1 min). Job status is kept in Redis for 1 hour.

---

## 2. Frontend → HuggingFace Static Space

HF Static Spaces serve pre-built files (no build step), so build locally and push `dist/`.

1. Point the build at the backend:
   ```bash
   cd frontend
   cp .env.production.example .env.production
   # edit .env.production: VITE_API_BASE=https://<your-render-service>.onrender.com
   npm install
   npm run build          # outputs dist/
   ```
2. Create a **Static** Space at huggingface.co/new-space (SDK: Static).
3. Put a `README.md` at the Space root with this frontmatter:
   ```
   ---
   title: Booking.ai Travel Planner
   emoji: ✈️
   colorFrom: blue
   colorTo: indigo
   sdk: static
   app_file: index.html
   pinned: false
   ---
   ```
4. Copy the **contents of `frontend/dist/`** (the `index.html` and `assets/` folder) into
   the Space repo root, next to that `README.md`, and push. The Space serves at
   `https://<user>-<space>.hf.space`.
5. Back on Render, make sure `ALLOWED_ORIGINS` includes that exact origin, then redeploy
   the backend so CORS allows the Space.

---

## Local development (unchanged)

`docker-compose up --build` runs Redis + the api + the frontend dev server. The frontend
dev server proxies `/api` to the backend, so `VITE_API_BASE` is not needed locally.
