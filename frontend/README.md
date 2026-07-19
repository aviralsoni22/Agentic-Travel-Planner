---
title: Booking.ai Travel Planner
emoji: ✈️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Booking.ai Travel Planner (frontend)

React + Vite frontend for the Agentic Travel Planner. HuggingFace builds the `Dockerfile`
here, which runs `npm run build` and serves the static bundle on port 7860.

## Configuration

Set one **Space variable** (Settings → Variables and secrets):

| Variable | Value |
|---|---|
| `VITE_API_BASE` | the deployed backend URL, e.g. `https://travel-planner-api-m8a2.onrender.com` |

It is baked into the bundle at build time, so **changing it requires a rebuild** (push again
or use "Factory rebuild"). The backend's `ALLOWED_ORIGINS` must include this Space's URL.

## Local dev

Run the whole stack from the repo root with `docker-compose up --build` instead; this folder's
dev server proxies `/api` to the backend and needs no `VITE_API_BASE`.
