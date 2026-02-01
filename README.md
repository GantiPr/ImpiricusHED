# Healthcare Engagement Dashboard

A full-stack application for managing physician messages and checking compliance against healthcare regulations.

## Tech Stack

**Backend**: Python, FastAPI, SQLAlchemy, SQLite  
**Frontend**: Next.js 14, React 18  
**Deployment**: Docker, Docker Compose

## Quick Start

### Local Development

**Backend:**
```bash
pip install -r backend/requirements.txt
python backend/load_data.py
cd backend && python -m uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Using Docker

```bash
docker-compose up --build
```

*Note: Requires Docker and Docker Compose to be installed.
https://www.docker.com/products/docker-desktop/*

## API Endpoints

- `GET /physicians` - List physicians (filter by state, specialty)
- `GET /messages` - List messages (filter by physician_id, dates, topic, sentiment, specialty, state, message text)
- `GET /messages/date-range` - Get min/max dates from message data
- `POST /classify/{message_id}` - Check message compliance against rules

## Design Overview

### Architecture
- **Backend**: RESTful API with FastAPI serving physician and message data from SQLite database
- **Frontend**: Single-page React application with search/filter interface and real-time compliance checking
- **Data**: CSV files loaded into SQLite, compliance rules defined in JSON

### Key Features
- **Multi-filter search**: Filter messages by physician, date range, topic, sentiment, specialty, state, and text
- **Compliance checking**: Classify messages against healthcare regulations (dosing safety, PHI protection, sample requests, clinical trials)
- **Joined data**: Messages display with full physician details (name, specialty, state)
- **Row highlighting**: Selected message highlighted for clarity
- **Dynamic date range**: Date pickers limited to available data range

### Project Structure
```
ImpiricusHED/
├── backend/
│   ├── app/              # FastAPI application
│   ├── tests/            # Unit tests (9 tests)
│   ├── load_data.py      # CSV to SQLite loader
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Backend container
├── frontend/
│   ├── app/              # Next.js pages
│   ├── package.json      # Node dependencies
│   └── Dockerfile        # Frontend container
├── data/
│   ├── physicians.csv    # Physician data (25 records)
│   ├── messages.csv      # Message data (200 records)
│   └── compliance_policies.json  # 5 compliance rules
└── docker-compose.yml    # Full stack orchestration
```

## Testing

```bash
cd backend
PYTHONPATH=. pytest tests/ -v
```

9 tests covering all API endpoints and compliance logic.
