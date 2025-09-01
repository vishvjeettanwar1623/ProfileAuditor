# ProfileAuditor

A application that verifies resume claims against online activity and generates a Reality Score.

## Features

- Resume upload and parsing (PDF/DOC)
- Skill and project extraction
- Verification against public data (GitHub, Twitter, LinkedIn)
- Reality Score generation (0-100)
- React dashboard with visualization of results
- Automated interview invites for top candidates

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Tailwind CSS
- **Resume Parsing**: PyPDF2/docx + spaCy/GPT
- **APIs**: GitHub API, Twitter API, Mock LinkedIn data
- **Email**: SendGrid API
- **Deployment**: Docker

## Project Structure

```
├── backend/               # FastAPI application
│   ├── app/              # Application code
│   │   ├── api/          # API routes
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utility functions
│   ├── tests/            # Backend tests
│   └── Dockerfile        # Backend Docker configuration
├── frontend/             # React application
│   ├── public/           # Static files
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── utils/        # Utility functions
│   └── Dockerfile        # Frontend Docker configuration
├── docker-compose.yml    # Docker Compose configuration
└── README.md            # Project documentation
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js and npm (for frontend development)
- Python 3.8+ (for backend development)

### Installation (Full stack with Docker)

1. Clone the repository
2. (Optional) Create and fill `.env` in the backend directory with any API keys if you plan to use real integrations:
   - GITHUB_TOKEN, TWITTER_BEARER_TOKEN, SENDGRID_API_KEY (see docker-compose.yml comments)
3. Build and start the application with Docker Compose:
   ```
   docker-compose up --build
   ```
4. Access the frontend at http://localhost:3000
5. Access the backend root at http://localhost:8000
6. API base is http://localhost:8000/api and docs at http://localhost:8000/docs

### How to run the backend only (Windows PowerShell)

You can run just the FastAPI backend without Docker.

1. Open PowerShell in the project root, then:
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. (Optional) Download the spaCy model locally. The code has a fallback that will try automatically, but this ensures it:
   ```powershell
   python -m spacy download en_core_web_sm
   ```
3. Start the server (hot-reload):
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```
4. Verify it’s running:
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs
   - API base: http://localhost:8000/api

Notes:
- The frontend expects the backend at http://localhost:8000. If you change the port, you’ll need to update any hardcoded URLs in the frontend (e.g., axios calls).
- If port 8000 is in use, you can pick another port by changing the uvicorn command (e.g., `--port 8001`).

### Run backend with Docker only

If you only want the backend via Docker (no frontend):

```powershell
# From the project root
docker-compose up --build backend
```

The backend will be available at http://localhost:8000

### Development Setup (manual)

#### Backend (Unix-like shells)
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## API Routes

- `POST /api/resume/upload` - Upload and parse resume
- `GET /api/verification/{resume_id}` - Get verification results
- `GET /api/score/{resume_id}` - Get reality score
- `POST /api/invite/{resume_id}` - Send interview invitation

## License

MIT
