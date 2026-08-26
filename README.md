# AI Opportunity Agent

AI-powered opportunity discovery, matching, notifications, and application tracking platform.

## Phase 1 local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
docker compose up -d postgres
alembic upgrade head
pytest
ruff check .
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Health check: `GET /health`

Database configuration is read from `DATABASE_URL` when supplied; otherwise the development PostgreSQL URL in `app/config.py` is used.

Project documentation and architecture are established on the `architecture` branch before subsequent implementation phases.
