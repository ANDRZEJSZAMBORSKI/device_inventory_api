# Device Inventory API

**EN** · [RU](README.md) · [PL](README.pl.md)

<!-- readme-preamble -->

**Device Inventory API** is a **Django** portfolio project: backend, database, REST API, Django-style testing, then **Docker / Docker Compose**, and **GitHub Actions**. It **continues** the training repo [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep): there you have a mock **Device Inventory** (`device_lab`, HTTP mocks, pytest, Allure, CI); **here** you build a **real** service with Django/DRF + **PostgreSQL**, same domain (devices, heartbeat, DFU, online/offline states).

| Track stage | Status on 2026-11-11 |
|-------------|----------------------|
| **D0** — bootstrap (venv, `startproject`, git) | in progress |
| **D1–D6, T1–T6, S1, T6b** | see [docs/PLAN.en.md](docs/PLAN.en.md) |

Full program: Django **without** DRF → models/ORM → Postgres/SQL → DRF → auth → Inventory API → pytest-django / APITestCase → **httpx** + Pydantic + Allure → **containers + GHA**.

### Who it is for

- Junior **Python / Backend / QA** who completed API automation in `hp-qa-junior-prep` and wants a **complete backend** for their resume.
- Anyone who wants a clear **mock → production-style API** story on one domain.

### Link to hp-qa-junior-prep

| hp-qa-junior-prep | device_inventory_api |
|-------------------|----------------------|
| `src/device_lab/` — in-memory + `MockTransport` | Django models + Postgres |
| `tests/device_lab/` (~76 tests) | `tests/` — TestCase, APITestCase, pytest-django, later httpx |
| Compose + MockServer + GHA | Compose **web + db + test job** + GHA in this repo |
| Pydantic `Device`, state machine | DRF serializers + same transitions (D5B) |

### Requirements

| Component | Note |
|-----------|------|
| Python | **≥ 3.11** (venv may use 3.14 — fine for learning) |
| Git | required from D0 |
| Docker Desktop | block **D6** (Compose) |
| PostgreSQL | block **S1** (local or container) |

### Documentation

| File | Language |
|------|----------|
| [docs/PLAN.md](docs/PLAN.md) | RU |
| [docs/PLAN.en.md](docs/PLAN.en.md) | EN — full D/T/S module plan |
| [docs/PLAN.pl.md](docs/PLAN.pl.md) | PL |

### Quick start (current stage D0)

```bash
cd /d/pyton_2/git/device_inventory_api
source .venv/Scripts/activate

python manage.py check
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` — Django welcome page. Secrets: copy `.env.example` → `.env` (`dotenv` wiring in **D1.2**).

### Target layout (grows module by module)

```text
device_inventory_api/
  config/
  apps/devices/, apps/accounts/
  tests/
  docs/
  docker-compose.yml
  .github/workflows/
```

Today: `config/`, `manage.py`, `requirements.txt`.

### End-of-track goals

- Device REST API + auth + heartbeat/DFU (parity with `device_lab`).
- **PostgreSQL** + sample SQL in `docs/SQL.md`.
- Tests: **Client**, **APITestCase**, **pytest-django**, **httpx** + Allure layer.
- **Docker Compose**: app + DB + test run.
- **GitHub Actions**: migrate → pytest → Allure artifact.

### Learning mode

Spec → you code and test → theory → review. Project/test logic is **not** changed by the assistant without your explicit OK (same as `hp-qa-junior-prep`).
