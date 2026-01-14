# Agentic AI Travel Planner 🌍✈️

A production-oriented multi-agent system powered by **CrewAI** that automates end-to-end travel planning. This system orchestrates 5 specialized AI agents to decompose user intent, search real-time data, and generate bookable itineraries with strict budget adherence.

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

## 🚀 The Solution: Autonomous Multi-Agent Orchestration

I built a **CrewAI-based architecture** that treats travel planning as a collaborative workflow between specialized agents. Unlike a standard chatbot, this system uses **Tool Calling** to interact with real-world APIs, ensuring that every suggestion is actually bookable and within budget.

### Key Features
* **5-Agent Architecture:** A dedicated team of agents (Manager, Flight Researcher, Hotel Researcher, Activity Booker and Budgeting Agent) works in parallel to build the plan.
* **Hallucination Guardrails:** Implemented strict **JSON/Pydantic schemas** to enforce structured outputs, reducing agent hallucinations by **~40%** and ensuring deterministic behavior.
* **Robust Tool Calling:** Custom interfaces for Flight, Hotel, and Activity searches that validate inputs before querying external APIs, ensuring reliable execution.
* **Resilient Workflows:** Engineered failure handling logic to manage API rate limits and missing data gracefully without crashing the user session.

---

## 🛠️ Tech Stack

* **Orchestration:** CrewAI
* **Backend:** Python, FastAPI, Uvicorn (Server)
* **Async Processing:** Celery, Redis (Broker & Backend)
* **Frontend:** React, Vite, TypeScript, Lucide React
* **Validation:** JSON Schema, Pydantic

---

## 🏗️ Architecture Overview

The system operates via a sequential process managed by CrewAI:
1.  **User Input:** Users fill a structured form (Origin, Destination, Dates, Budget, Interests) via the React UI.
2.  **Decomposition:** The Manager Agent breaks this into sub-tasks (Flight Search, Hotel Search, Itinerary Building).
3.  **Execution:** Specialized agents use custom tools to fetch live data.
4.  **Validation:** The Budget Agent reviews the final package against the user's constraints.
5.  **Output:** A structured JSON response rendered via the React frontend.

---

## ⚡ Getting Started

### Prerequisites
* **System**: Python 3.10+, Node.js 18+, Docker Desktop
* **API Keys**: OpenAI, RapidAPI (Booking.com), Geoapify.

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/aviralsoni22/agentic-travel-planner.git
cd agentic-travel-planner
```

#### 2. Configure Environment
Create a `.env` file in the `agentic_travel_planner` directory (backend) and add your keys:
```bash
# agentic_travel_planner/.env
MODEL=gpt-4o
OPENAI_API_KEY=sk-...
CREWAI_TRACING_ENABLED=true
RAPIDAPI_KEY=...
GEOAPIFY_KEY=...
REDIS_URL=redis://redis:6379/0  # Note: Host is 'redis' inside Docker
```
Create a `.env.local` file in the `frontend` directory (frontend) and add your keys:
```bash
# frontend/.env
VITE_GEMINI_API_KEY= ...
```

#### 3. Run Backend (Docker 🐳)
This project requires Docker to orchestrate the AI Agents, API and Redis (used for both message queuing and result storage).

```bash
# From the root directory
docker-compose up --build
```
*Wait until you see "Application startup complete" in the logs.*

#### 4. Frontend Setup (React)
Open a new terminal to run the UI:
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

#Run this command
npm run dev

```
Visit the link in the frontend terminal to start planning!