# OMS Trade Lifecycle Validation — Automated QA Framework

End-to-end automated QA framework for an Order Management System (OMS), validating the
complete trade lifecycle using **Python + pytest** and a lightweight **Flask** simulation backend
backed by **PostgreSQL**.

---

## Architecture

```
┌─────────────────────────────────────────┐
│          Test Suites (pytest)           │
│  functional / regression / integration  │
└────────────────┬────────────────────────┘
                 │ HTTP (Flask test client)
┌────────────────▼────────────────────────┐
│          Flask OMS Simulation           │
│  POST/GET/PATCH/DELETE /orders          │
│  State machine enforcement              │
└────────────────┬────────────────────────┘
                 │ SQLAlchemy ORM
┌────────────────▼────────────────────────┐
│            PostgreSQL                   │
│  orders table · indexes · constraints   │
└─────────────────────────────────────────┘
```

### Order Lifecycle States

```
NEW → PENDING_ROUTING → ROUTED → EXECUTED
 ↓           ↓             ↓
CANCELLED  CANCELLED   CANCELLED
 ↓           ↓             ↓
REJECTED   REJECTED    REJECTED
```

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.12+

### 1. Start the database

```bash
docker-compose up -d postgres postgres_test
```

### 2. Install dependencies

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

### 4. Run all tests

```bash
pytest tests/ -v
```

### 5. Run with coverage report

```bash
pytest tests/ -v --cov=app --cov-report=html
open htmlcov/index.html
```

### 6. Run a specific suite

```bash
pytest tests/functional/ -v
pytest tests/regression/ -v
pytest tests/integration/ -v
```

---

## Test Coverage

| Suite | Tests | Validates |
|---|---|---|
| Functional | 36 | Order creation, routing, validation, execution, modification, cancellation |
| Regression | 13 | State machine transitions, duplicate/idempotency detection |
| Integration | 16 | DB ↔ API consistency, 15+ data integrity defect scenarios |
| **Total** | **65+** | |

---

## CI/CD

GitHub Actions runs the full test suite on every push and pull request.
See [.github/workflows/ci.yml](.github/workflows/ci.yml).

---

## Project Structure

```
oms-trade-lifecycle-qa/
├── app/                    # Flask OMS simulation (system under test)
├── tests/
│   ├── functional/         # Happy-path & error-path per lifecycle stage
│   ├── regression/         # State machine & duplicate detection
│   ├── integration/        # DB consistency & invalid scenario coverage
│   └── utils/              # Shared API client and DB assertion helpers
├── sql/                    # Schema DDL and seed data
├── docker-compose.yml
└── pytest.ini
```
