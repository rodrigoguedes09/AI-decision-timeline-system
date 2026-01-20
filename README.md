# AI Decision Timeline

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)

> **Making AI decisions visible, traceable, and understandable**

---

## The Problem

**AI decisions are opaque and hard to debug.**

When an AI system makes a decision—approving a loan, rejecting content, routing a customer request — we rarely see *how* it arrived at that conclusion. Was it a rule? An LLM? What context influenced it? What if we need to audit or explain it later?

Traditional logging treats decisions as text entries. This project treats them as **structured, visual, temporal events** that can be inspected, replayed, and understood by anyone.

---

## The Solution

**AI Decision Timeline** is a visual-first system that captures every step of an AI decision process and displays it as an interactive timeline.

Each decision is broken into clear stages:
- **Input** — What data triggered the decision?
- **Reasoning** — How did the system think through it?
- **Decision** — What was chosen and why?
- **Action** — What happened as a result?
- **Outcome** — What was the final result?

You can **replay any decision step-by-step**, like debugging code or watching a video frame-by-frame.

**Main screen of the application:**
<p align="center">
  <img src="https://github.com/user-attachments/assets/e2a824f9-5168-4913-a852-cb5535cf894f" width="800" />
</p>

**"Replay Decision"** - Analysing Model decisions and data:
<p align="center">
  <img src="https://github.com/user-attachments/assets/9294a35a-2f17-46ff-98ba-58b74d96fb95" width="800" />
</p>

---

##  Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+

### One-Command Setup

**Windows:**
```powershell
.\setup.ps1
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### Start the Application

**Windows:**
```powershell
.\start.ps1
```

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

Then open your browser to: **http://localhost:3000**

### Stop the Application

**Windows:**
```powershell
.\stop.ps1
```

**macOS/Linux:**
```bash
./stop.sh
```

---

### Manual Setup (Alternative)

```bash
# Clone the repository
git clone https://github.com/rodrigoguedes09/AI-decision-timeline-system.git
cd AI-decision-timeline-system

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/load_demo_data.py

# Run backend
uvicorn app.main:app --reload --port 8001
uvicorn app.main:app --reload

# In another terminal, install frontend dependencies
cd ../frontend
npm install

# Run frontend
npm run dev
```

### Using Demo Data

The system comes with realistic demo scenarios:

```bash
cd backend
python scripts/load_demo_data.py
```

This loads example decisions for:
-  Customer support routing
-  Loan approval process
-  Content moderation
-  System fallback scenarios

---

##  Architecture

```

                   FRONTEND (React)                   
       
     Timeline      Replay Mode      Filters   
       View          (Key UX)       & Search  
       

                         
                          REST API
                         

                BACKEND (FastAPI)                     
    
             Decision Trace Engine                
    - Event creation & storage                    
    - Step sequencing                             
    - Confidence tracking                         
    
    
                Data Layer                        
    - SQLAlchemy ORM                              
    - PostgreSQL / SQLite                         
    

```

### Key Components

- **Decision Trace Model**: Structured representation of AI decisions
- **Step Sequencing**: Ordered steps (input → reasoning → decision → action → outcome)
- **REST API**: Create, retrieve, and query decision timelines
- **Timeline UI**: Visual representation with color-coded steps
- **Replay Engine**: Step-by-step decision playback

---

##  Decision Structure

Each decision event captures:

```json
{
  "decision_id": "dec_1234567890",
  "timestamp": "2026-01-20T14:30:00Z",
  "input_data": {
    "user_id": "user_456",
    "request_type": "refund",
    "amount": 99.99
  },
  "system_state": {
    "user_tier": "premium",
    "previous_refunds": 1,
    "account_age_days": 365
  },
  "reasoning": "User is premium tier with good history. Amount within auto-approval limit.",
  "decision": "approve_refund",
  "confidence": 0.92,
  "source": "hybrid",
  "steps": [
    {
      "step_type": "input",
      "content": "Refund request received: $99.99",
      "timestamp": "2026-01-20T14:30:00Z"
    },
    {
      "step_type": "reasoning",
      "content": "Checking user tier and history...",
      "metadata": {"rule_matched": "premium_auto_approval"},
      "timestamp": "2026-01-20T14:30:01Z"
    },
    {
      "step_type": "decision",
      "content": "Approved",
      "metadata": {"confidence": 0.92},
      "timestamp": "2026-01-20T14:30:02Z"
    },
    {
      "step_type": "action",
      "content": "Refund processed to original payment method",
      "timestamp": "2026-01-20T14:30:03Z"
    },
    {
      "step_type": "outcome",
      "content": "Success - Refund completed",
      "timestamp": "2026-01-20T14:30:05Z"
    }
  ]
}
```

---

##  Replay Mode (Key Feature)

The **Replay** feature lets you see exactly how a decision unfolded:

1. Click any decision card in the timeline
2. Steps are displayed in chronological order
3. See timestamps, metadata, and reasoning at each stage
4. Click on any step to view its details

This is like a **debugger for AI behavior**.

---

##  Color Coding

Steps are visually differentiated:

- **Blue** — Input (data entering the system)
- **Purple** — Reasoning (AI thinking process)
- **Green** — Decision (approved/accepted)
- **Red** — Decision (rejected/blocked)
- **Yellow** — Action (system executing)
- **Gray** — Outcome (final result)

---

##  Project Structure

```
AI-decision-timeline-system/
 backend/
    app/
       main.py              # FastAPI app
       models.py            # SQLAlchemy models
       schemas.py           # Pydantic schemas
       database.py          # DB setup
       routers/
          decisions.py     # Decision endpoints
          traces.py        # Trace endpoints
       services/
           decision_engine.py
           trace_builder.py
    scripts/
       load_demo_data.py
    requirements.txt
    tests/
 frontend/
    src/
       components/
          Timeline.jsx
          DecisionCard.jsx
          ReplayMode.jsx
       services/
          api.js
       App.jsx
    package.json
    vite.config.js
 docs/
    demo.gif
 README.md
```

---

##  API Examples

### Create a Decision

```bash
POST /api/decisions
Content-Type: application/json

{
  "input_data": {"user_query": "Can I get a refund?"},
  "system_state": {"user_tier": "premium"},
  "reasoning": "Premium users eligible for auto-refund",
  "decision": "approve",
  "confidence": 0.95,
  "source": "rule"
}
```

### Get Timeline

```bash
GET /api/decisions?limit=20&sort=desc
```

### Replay Decision

```bash
GET /api/decisions/{decision_id}/replay
```

---

##  Technologies

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: React, Axios, CSS3
- **Deployment**: Docker, Docker Compose

---

##  License

MIT License - see [LICENSE](LICENSE) for details.

---

**Made with  by [Rodrigo Guedes](https://github.com/rodrigoguedes09)**
