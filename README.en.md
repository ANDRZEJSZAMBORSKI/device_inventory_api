# Device Inventory API

**EN** · [RU](README.md) · [PL](README.pl.md)

<!-- readme-preamble -->

**Device Inventory API** is an end-to-end **Django** codebase: HTTP layer, persistence (SQLite → PostgreSQL), **Django REST Framework**, device inventory domain, automated testing, containerization, and continuous integration. It continues [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep): the mock `device_lab` layer is implemented here as a **production-style backend** (device states, heartbeat, firmware update flows).

This document is both a **runbook** (commands, layout, tests) and a **technical guide** to Django architecture tied to source files. Languages: [RU](README.md), **EN** (this file), [PL](README.pl.md). Full curriculum: [docs/PLAN.en.md](docs/PLAN.en.md).

### System purpose

| Layer | Responsibility |
|-------|----------------|
| **Django (MTV)** | HTTP routing, views, ORM, admin |
| **PostgreSQL** | Primary store after the persistence module |
| **DRF** | REST, serialization, authentication, pagination |
| **Test stack** | `Client`, `APITestCase`, `pytest-django`, **httpx** |
| **Delivery** | Docker Compose, GitHub Actions |

### hp-qa-junior-prep alignment

| hp-qa (mock / QA) | This repository |
|-------------------|-----------------|
| `InMemoryInventory`, `MockTransport` | ORM + Postgres transactions |
| Pydantic `Device`, state FSM | DRF + domain rules |
| `tests/device_lab/` | `tests/api/`, httpx integration |
| Compose, GHA | web + db Compose, CI workflows |

### Requirements

Python ≥ 3.11, Django 5.2.x (`requirements.txt`), Git, Docker and PostgreSQL in later modules.

### Quick start

```bash
cd /d/pyton_2/git/device_inventory_api
source .venv/Scripts/activate
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py runserver
```

Tests (module D1):

```bash
python manage.py test tests.test_health -v 2
```

### Repository layout

`config/` — project settings and root URLconf. `core/` — first app with views and routes. `tests/` — project-level test suite. `docs/` — curriculum (PLAN).

### Module D1 — HTTP and MTV

**MTV:** Model (data), Template (presentation), View (request handling). Current revision: View-only (`core.views.health`); domain models follow in the ORM module.

**Request flow:** Client → middleware → URL resolver → `health(request)` → `JsonResponse`.

**HttpRequest** carries method, path, query (`QueryDict`), body, headers, `META`, user, session. The `/health/` endpoint exposes a structured snapshot for development observability and regression tests.

**JsonResponse** covers deterministic JSON; **DRF** is introduced for CRUD REST.

### GET /health/ contract

| Item | Value |
|------|--------|
| Method | GET |
| Path | `/health/` |
| Route name | `health` |
| Status | 200 |
| Header | `X-API-Version: 1.0` |
| Body | `status: ok` plus structured request mirror fields |

Repeated query keys appear as lists in `GET`. Production health endpoints are typically minimal; this revision is diagnostic by design.

### URL routing

`config/urls.py`: `admin/` + `include("core.urls")`. `core/urls.py`: `health/` → `views.health`. `include()` keeps per-app URL modules decoupled.

### django.test.Client

Runs the full Django stack in-process without a listening socket—not a view mock. Contrasts with **httpx**, which targets a real HTTP listener (`runserver`, `live_server`, or Compose).

`tests/test_health.py` covers bare GET, query parameters, repeated keys, and `QueryDict` semantics.

### Curriculum

See **[docs/PLAN.en.md](docs/PLAN.en.md)** for module sequence: D0 → D1/T1 → D2/T2 → S1 → DRF blocks → httpx/Allure → Compose/GHA.

**Implemented:** D0 bootstrap, D1 `/health/`, T1 `test_health`.

### References

- https://github.com/ANDRZEJSZAMBORSKI/device_inventory_api  
- https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep  
- https://docs.djangoproject.com/en/5.2/
