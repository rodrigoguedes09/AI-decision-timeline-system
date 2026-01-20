# AI Decision Timeline - Quick Start Guide

##  Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/rodrigoguedes09/AI-decision-timeline-system.git
cd AI-decision-timeline-system
```

### Step 2: Set Up the Backend
```bash
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Load demo data (optional but recommended)
python scripts/load_demo_data.py

# Start the backend server
uvicorn app.main:app --reload
```

The backend will be available at: http://localhost:8000

API documentation: http://localhost:8000/docs

### Step 3: Set Up the Frontend
Open a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at: http://localhost:3000

---

##  Using the System

### 1. **View the Timeline**
- Open http://localhost:3000
- You'll see all decisions in chronological order
- Each card shows key information: decision, confidence, source, outcome

### 2. **Replay a Decision**
- Click any decision card
- A modal opens showing step-by-step replay
- Click "Play" to see the decision unfold automatically
- Or click individual steps to jump to them

### 3. **Filter Decisions**
- Use the filter bar at the top
- Filter by source (rule/LLM/hybrid/manual)
- Filter by minimum confidence level
- Sort by newest or oldest first

### 4. **View Statistics**
- Dashboard at the top shows:
  - Total decisions
  - Average confidence
  - Low confidence warnings
  - Breakdown by source

---

##  Creating Your Own Decisions

### Using the API (Python Example)
```python
import requests

decision_data = {
    "input_data": {
        "user_id": "user_789",
        "request_type": "refund",
        "amount": 49.99
    },
    "system_state": {
        "user_tier": "standard",
        "account_age_days": 120
    },
    "reasoning": "Standard user with good history. Amount within limit.",
    "decision": "approve_refund",
    "confidence": 0.88,
    "source": "rule",
    "tags": ["refund", "auto_approved"]
}

response = requests.post(
    "http://localhost:8000/api/decisions",
    json=decision_data
)

print(response.json())
```

### Using cURL
```bash
curl -X POST "http://localhost:8000/api/decisions" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {"user_query": "I need help"},
    "reasoning": "Query requires human support",
    "decision": "route_to_human",
    "confidence": 0.92,
    "source": "hybrid",
    "tags": ["support"]
  }'
```

---

##  Using Docker (Alternative Setup)

If you prefer Docker:

```bash
# Build and start all services
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Database: PostgreSQL on port 5432
```

---

##  Running Tests

```bash
cd backend
pytest
```

---

##  Configuration

### Backend Environment Variables
Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=sqlite:///./ai_decisions.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/ai_decisions
```

### Frontend Environment Variables
Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000/api
```

---

##  Next Steps

1. **Explore the demo data** - See realistic decision scenarios
2. **Create your own decisions** - Use the API to log decisions from your system
3. **Integrate with your AI** - Connect your LLM or rule engine
4. **Customize the UI** - Modify colors, layouts, or add new features

---

##  Troubleshooting

### Backend won't start
- Check Python version: `python --version` (must be 3.9+)
- Verify dependencies: `pip install -r requirements.txt`
- Check if port 8000 is available

### Frontend won't start
- Check Node version: `node --version` (must be 16+)
- Delete `node_modules` and run `npm install` again
- Check if port 3000 is available

### No decisions showing
- Make sure backend is running
- Load demo data: `python scripts/load_demo_data.py`
- Check browser console for errors

---

##  Tips

- **Start with demo data** - It's the fastest way to see the system in action
- **Keep the backend running** - The frontend needs it to fetch data
- **Use the API docs** - Visit http://localhost:8000/docs for interactive API testing
- **Experiment with replay** - It's the most impressive feature!

---

**Need help?** Open an issue on GitHub or check the [README](README.md) for more details.
