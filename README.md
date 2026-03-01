# BlackRoad Notebook Server

[![CI](https://github.com/BlackRoad-Labs/blackroad-notebook-server/actions/workflows/ci.yml/badge.svg)](https://github.com/BlackRoad-Labs/blackroad-notebook-server/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-proprietary-red)](#license)
[![npm](https://img.shields.io/badge/npm-ready-cb3837?logo=npm)](https://www.npmjs.com/)
[![Stripe](https://img.shields.io/badge/stripe-integrated-635bff?logo=stripe)](https://stripe.com/)

> **Production-grade Jupyter notebook server with AI kernels, SQLite persistence, and multi-format export — the computational core of the [BlackRoad OS](https://blackroadlabs.com) platform.**

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Requirements](#requirements)
5. [Installation](#installation)
   - [Python (pip)](#python-pip)
   - [Node.js / npm Client](#nodejs--npm-client)
6. [Quick Start](#quick-start)
7. [CLI Reference](#cli-reference)
   - [create](#create)
   - [list](#list)
   - [execute](#execute)
   - [export](#export)
   - [history](#history)
   - [kernels](#kernels)
8. [Python API Reference](#python-api-reference)
9. [Database Schema](#database-schema)
10. [Stripe Billing Integration](#stripe-billing-integration)
11. [Environment Variables](#environment-variables)
12. [Testing](#testing)
    - [Unit Tests](#unit-tests)
    - [End-to-End (E2E) Tests](#end-to-end-e2e-tests)
13. [CI / CD](#ci--cd)
14. [Production Deployment](#production-deployment)
15. [Security](#security)
16. [Contributing](#contributing)
17. [License](#license)

---

## Overview

**BlackRoad Notebook Server** is the execution engine behind the BlackRoad OS interactive computing platform. It provides a lightweight, dependency-minimal Jupyter-compatible notebook backend that can be embedded in any Python or Node.js application, deployed as a standalone microservice, or billed per-execution via Stripe.

Key differentiators:

- **Zero broker required** — runs entirely on SQLite; no Redis, no RabbitMQ.
- **AI-kernel ready** — kernel registry allows drop-in registration of custom AI/ML runtimes.
- **npm-consumable** — exposes a clean JSON CLI so Node.js services can shell out or wrap it as an npm package.
- **Stripe-native billing** — every execution record carries the metadata required to feed a Stripe usage-based billing pipeline.

---

## Features

| Feature | Status |
|---|---|
| Create, load, and delete notebooks | ✅ |
| Execute cells (single or all) | ✅ |
| SQLite-backed persistence (WAL mode) | ✅ |
| Multi-format export: `.ipynb`, `.py`, `.html` | ✅ |
| Execution history with timing | ✅ |
| Custom kernel registration | ✅ |
| Stripe usage-record emission | ✅ |
| npm JSON CLI | ✅ |
| CI on Python 3.11 & 3.12 | ✅ |

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                  BlackRoad OS Platform                │
│                                                      │
│  ┌─────────────┐   JSON CLI / HTTP   ┌────────────┐  │
│  │  Node.js /  │ ──────────────────▶ │  Notebook  │  │
│  │  npm client │ ◀────────────────── │   Server   │  │
│  └─────────────┘                     │  (main.py) │  │
│                                      └─────┬──────┘  │
│  ┌─────────────┐                           │         │
│  │   Stripe    │ ◀── usage records ────────┤         │
│  │  Billing    │                           │         │
│  └─────────────┘                     ┌─────▼──────┐  │
│                                      │   SQLite   │  │
│                                      │  (WAL DB)  │  │
│                                      └────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## Requirements

- **Python** 3.11 or higher
- **pip** packages: `jupyter`, `nbconvert` (optional, for advanced HTML export)
- **Node.js** 18+ (optional, for npm client wrapper)
- **Stripe account** (optional, for metered billing)

---

## Installation

### Python (pip)

```bash
# Install runtime dependencies
pip install jupyter nbconvert

# Clone the repository
git clone https://github.com/BlackRoad-Labs/blackroad-notebook-server.git
cd blackroad-notebook-server

# Run the server CLI
python main.py --help
```

### Node.js / npm Client

The notebook server exposes a pure JSON CLI, making it trivially wrappable from Node.js or any npm package:

```js
// npm install @blackroad/notebook-client  -- coming soon
const { execSync } = require('child_process');

function listNotebooks() {
  const raw = execSync('python main.py list').toString();
  return JSON.parse(raw);
}

function createNotebook(name, path) {
  const raw = execSync(`python main.py create "${name}" "${path}"`).toString();
  return JSON.parse(raw);
}
```

> 📦 An official `@blackroad/notebook-client` npm package that wraps this CLI is on the roadmap. Star the repo to be notified.

---

## Quick Start

```bash
# 1. Create a notebook
python main.py create "My First Notebook" notebooks/demo.ipynb

# 2. List all notebooks
python main.py list

# 3. Execute all cells
python main.py execute <notebook-id>

# 4. Export to Python script
python main.py export <notebook-id> --format script

# 5. View execution history
python main.py history <notebook-id>

# 6. List registered kernels
python main.py kernels
```

---

## CLI Reference

All commands emit JSON to stdout (except `execute` and `export` which emit human-readable progress). Exit code `0` = success, non-zero = error.

### `create`

Create a new notebook and persist it to the database.

```
python main.py create <name> <path> [--kernel KERNEL]
```

| Argument | Description | Default |
|---|---|---|
| `name` | Display name for the notebook | required |
| `path` | File path (e.g. `notebooks/demo.ipynb`) | required |
| `--kernel` | Kernel name to associate | `python3` |

**Output:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My First Notebook",
  "path": "/absolute/path/notebooks/demo.ipynb"
}
```

---

### `list`

List all notebooks ordered by last update.

```
python main.py list
```

**Output:** JSON array of notebook objects.

---

### `execute`

Execute one or all code cells in a notebook.

```
python main.py execute <id> [--cell INDEX] [--timeout SECONDS]
```

| Argument | Description | Default |
|---|---|---|
| `id` | Notebook ID | required |
| `--cell` | Execute a single cell by zero-based index | all cells |
| `--timeout` | Per-cell timeout in seconds | `60` |

**Output:**
```
✓ Cell 0 [success] (42ms)
   Hello, world!
✗ Cell 1 [error] (5ms)
   NameError: name 'x' is not defined
```

---

### `export`

Export a notebook to a file.

```
python main.py export <id> [--format {ipynb,html,script}]
```

| Format | Output |
|---|---|
| `ipynb` | Standard Jupyter notebook (default) |
| `html` | Standalone HTML page |
| `script` | Python `.py` script with cell comments |

---

### `history`

Show execution history for a notebook.

```
python main.py history <id> [--limit N]
```

| Argument | Description | Default |
|---|---|---|
| `id` | Notebook ID | required |
| `--limit` | Maximum records to return | `50` |

---

### `kernels`

List all registered kernels.

```
python main.py kernels
```

---

## Python API Reference

Import `JupyterService` directly for programmatic use:

```python
from main import JupyterService, init_db

init_db()
svc = JupyterService()

# Create
nb = svc.notebook_create("Demo", "notebooks/demo.ipynb", kernel="python3")

# Load
nb = svc.notebook_load(nb.id)

# Execute
results = svc.notebook_execute(nb.id, timeout=30)

# Export
path = svc.notebook_export(nb.id, fmt="html")

# History
history = svc.execution_history(nb.id, limit=10)

# Delete
svc.notebook_delete(nb.id)

# Kernels
svc.register_kernel("gpt-kernel", "python", "GPT-4 Kernel", ["python", "-m", "gpt_kernel"])
kernels = svc.list_kernels()
```

---

## Database Schema

The server uses a single SQLite database (WAL mode for concurrent reads).

```sql
-- Notebooks
CREATE TABLE notebooks (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    path        TEXT NOT NULL UNIQUE,
    kernel      TEXT NOT NULL DEFAULT 'python3',
    created_at  TEXT NOT NULL,  -- ISO-8601 UTC
    updated_at  TEXT NOT NULL,  -- ISO-8601 UTC
    cell_count  INTEGER NOT NULL DEFAULT 0,
    metadata    TEXT NOT NULL DEFAULT '{}'
);

-- Execution records (feeds Stripe usage billing)
CREATE TABLE executions (
    id           TEXT PRIMARY KEY,
    notebook_id  TEXT NOT NULL REFERENCES notebooks(id) ON DELETE CASCADE,
    cell_index   INTEGER NOT NULL,
    source       TEXT NOT NULL,
    output       TEXT,
    status       TEXT NOT NULL DEFAULT 'pending',  -- pending | success | error | timeout
    started_at   TEXT,
    finished_at  TEXT,
    duration_ms  INTEGER     -- billable unit for Stripe metered billing
);

-- Custom kernel registry
CREATE TABLE kernels (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE,
    language     TEXT NOT NULL,
    display_name TEXT NOT NULL,
    argv         TEXT NOT NULL,    -- JSON array
    created_at   TEXT NOT NULL
);

CREATE INDEX idx_exec_nb ON executions(notebook_id);
```

---

## Stripe Billing Integration

BlackRoad Notebook Server is designed to plug directly into [Stripe Metered Billing](https://stripe.com/docs/billing/subscriptions/metered-usage).

Each `Execution` row records `duration_ms`, `status`, and `notebook_id` — exactly the fields needed to emit a Stripe usage record:

```python
import stripe
from main import JupyterService, init_db

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
init_db()
svc = JupyterService()

# Execute cells
results = svc.notebook_execute(notebook_id)

# Report usage to Stripe
for result in results:
    if result.status == "success":
        stripe.SubscriptionItem.create_usage_record(
            subscription_item_id=os.environ["STRIPE_SUBSCRIPTION_ITEM_ID"],
            quantity=1,                          # 1 cell execution
            timestamp=int(result.started_at_ts), # Unix timestamp
            action="increment",
        )
```

### Stripe Environment Variables

| Variable | Description |
|---|---|
| `STRIPE_SECRET_KEY` | Your Stripe secret key (`sk_live_…` or `sk_test_…`) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key for frontend |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret for event verification |
| `STRIPE_SUBSCRIPTION_ITEM_ID` | The metered subscription item to record usage against |

> 🔐 **Never commit Stripe keys to source control.** Use environment variables or a secrets manager.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `NOTEBOOK_DB` | Path to the SQLite database file | `~/.blackroad/notebooks.db` |
| `STRIPE_SECRET_KEY` | Stripe secret key for billing | — |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | — |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | — |
| `STRIPE_SUBSCRIPTION_ITEM_ID` | Stripe metered subscription item | — |

---

## Testing

### Unit Tests

Run the full unit test suite:

```bash
python -m pytest test_notebook_server.py -v
```

Tests cover:

| Test | Description |
|---|---|
| `TestCell.test_to_ipynb_code` | Code cell serialisation |
| `TestCell.test_to_ipynb_markdown` | Markdown cell serialisation |
| `TestCell.test_from_ipynb_list_source` | Parsing list-form source |
| `TestJupyterService.test_notebook_create_and_load` | Create + round-trip load |
| `TestJupyterService.test_notebook_create_with_cells` | Cell persistence |
| `TestJupyterService.test_notebook_execute_success` | Successful cell execution |
| `TestJupyterService.test_notebook_execute_error` | Error cell execution |
| `TestJupyterService.test_notebook_export_script` | Python script export |
| `TestJupyterService.test_notebook_list` | Notebook listing |
| `TestJupyterService.test_execution_history` | History retrieval |

### End-to-End (E2E) Tests

Run a full end-to-end workflow from the CLI:

```bash
# 1. Create a notebook
ID=$(python main.py create "E2E Test" /tmp/e2e_test.ipynb | python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 2. Verify it appears in the list
python main.py list | python -c "
import sys, json
nbs = json.load(sys.stdin)
assert any(n['id'] == '$ID' for n in nbs), 'Notebook not in list'
print('List check passed ✓')
"

# 3. Execute (empty notebook — no cells to run)
python main.py execute "$ID"

# 4. Export all formats
python main.py export "$ID" --format ipynb
python main.py export "$ID" --format script
python main.py export "$ID" --format html

# 5. Check history
python main.py history "$ID"

# 6. List kernels
python main.py kernels

echo "E2E PASSED ✓"
```

---

## CI / CD

GitHub Actions runs the test matrix automatically on every push and pull request:

```yaml
# .github/workflows/ci.yml
strategy:
  matrix:
    python-version: ["3.11", "3.12"]
```

[![CI](https://github.com/BlackRoad-Labs/blackroad-notebook-server/actions/workflows/ci.yml/badge.svg)](https://github.com/BlackRoad-Labs/blackroad-notebook-server/actions/workflows/ci.yml)

---

## Production Deployment

### Standalone Process

```bash
# Set database path to a persistent volume
export NOTEBOOK_DB=/var/data/blackroad/notebooks.db

# Run a command
python main.py list
```

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir jupyter nbconvert
ENV NOTEBOOK_DB=/data/notebooks.db
VOLUME ["/data"]
ENTRYPOINT ["python", "main.py"]
```

```bash
docker build -t blackroad-notebook-server .
docker run -v notebooks_data:/data blackroad-notebook-server list
```

### Systemd Service

```ini
[Unit]
Description=BlackRoad Notebook Server
After=network.target

[Service]
User=blackroad
Environment=NOTEBOOK_DB=/var/data/blackroad/notebooks.db
Environment=STRIPE_SECRET_KEY=sk_live_...
ExecStart=/usr/bin/python3 /opt/blackroad/main.py list
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Security

- All notebook IDs are UUIDv4 — non-guessable.
- Cell execution runs in an isolated subprocess (not `eval`).
- The SQLite database uses WAL mode and foreign-key cascades for data integrity.
- Stripe keys are consumed from environment variables only — never hardcoded.
- Input paths are resolved with `Path.resolve()` to prevent directory traversal.

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/my-feature`.
3. Add tests for your changes.
4. Run `python -m pytest test_notebook_server.py -v` and ensure all tests pass.
5. Open a pull request against `main`.

---

## License

Proprietary — © BlackRoad Labs. All rights reserved.

See [LICENSE](LICENSE) for full terms.
