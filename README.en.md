# Device Inventory API

**EN** · [RU](README.md) · [PL](README.pl.md)

<!-- readme-preamble -->

**Device Inventory API** is an end-to-end **Django** codebase: HTTP layer, persistence (SQLite → PostgreSQL), **Django REST Framework**, device inventory domain, automated testing, containerization, and continuous integration. It continues [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep): the mock `device_lab` layer becomes a **real backend** (device states, heartbeat, firmware update flows).

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
| Pydantic `Device`, state FSM | Django `Device` + DRF rules (later) |
| `tests/device_lab/` | `tests/test_device_model.py`, later `tests/api/` |
| Compose, GHA | web + db Compose, CI workflows |

### Requirements

| Component | Version / note |
|-----------|----------------|
| Python | ≥ 3.11 |
| Django | 5.2.x (`requirements.txt`) |
| Git | versioning and CI |
| PostgreSQL | optional until module S1 (`DB_ENGINE=postgresql`) |
| Docker | late module D6 |

### Documentation map

| README section | Topic | Code |
|----------------|-------|------|
| [Quick start](#quick-start) | venv, migrate, tests | repo root |
| [Layout](#repository-layout) | `config`, `core`, `inventory`, `tests` | — |
| [D1 — HTTP / MTV](#module-d1--http-and-mtv) | views, `JsonResponse` | `core/` |
| [D1.2 — config](#module-d12--configuration-12-factor) | `.env`, secrets | `config/settings.py` |
| [D1.3 — routing](#module-d13--named-routes) | `reverse`, `resolve` | `tests/test_routing.py` |
| [Database](#database-configuration-db_engine) | `DB_ENGINE` | `.env.example` |
| [D2 — Device ORM](#module-d2--orm-and-device-model) | model, migrations | `inventory/models.py` |
| [T2 — ORM tests](#module-t21--orm-testing) | `TestCase`, transactions | `tests/test_device_model.py` |

### Table of contents

1. [Quick start](#quick-start)
2. [Repository layout](#repository-layout)
3. [Module D1 — HTTP and MTV](#module-d1--http-and-mtv)
4. [GET /health/ contract](#get-health-contract)
5. [URL routing](#url-routing)
6. [django.test.Client](#djangotestclient)
7. [Module D1.2 — configuration](#module-d12--configuration-12-factor)
8. [Module D1.3 — named routes](#module-d13--named-routes)
9. [GET /version/ contract](#get-version-contract)
10. [Database configuration](#database-configuration-db_engine)
11. [Module D2 — ORM and Device](#module-d2--orm-and-device-model)
12. [Module T2.1 — ORM testing](#module-t21--orm-testing)
13. [Test commands](#test-commands)
14. [Curriculum status](#curriculum-status)
15. [Next steps](#next-steps)

---

## Quick start

```bash
cd /d/pyton_2/git/device_inventory_api
source .venv/Scripts/activate
pip install -r requirements.txt

cp .env.example .env
# Set DJANGO_SECRET_KEY and DB_ENGINE (see configuration sections)

python manage.py check
python manage.py migrate
python manage.py runserver
```

Smoke HTTP:

```bash
curl -s http://127.0.0.1:8000/health/ | head
```

Regression (HTTP + routing + ORM on SQLite):

```bash
python manage.py test tests.test_device_model tests.test_routing tests.test_health -v 2
```

ORM smoke in shell:

```bash
python manage.py shell -c "from inventory.models import Device; d=Device.objects.create(); print(d.device_id, d.state)"
```

The project **refuses to start** without `DJANGO_SECRET_KEY` or valid `DB_ENGINE` (`ValueError` in settings) by design.

---

## Repository layout

```text
device_inventory_api/
  config/                 # settings, root urlconf, WSGI/ASGI
  core/                   # HTTP: health, version
  inventory/              # domain: Device model, migrations (D2)
    models.py
    migrations/
  tests/
    test_health.py        # D1 / T1
    test_routing.py       # D1.3
    test_device_model.py  # D2/T2 + transaction lab (part PostgreSQL-only)
  .env.example
  docs/PLAN*.md
  manage.py
  requirements.txt
```

`config/` — project configuration. `core/` — infrastructure HTTP. `inventory/` — device domain. `tests/` — project-level regression (not inside `startapp`).

Root urlconf reserves **`/inventory/`** via `include("inventory.urls")`; REST routes arrive in D3–D5.

---

## Module D1 — HTTP and MTV

**MTV:** Model (data), Template (presentation), View (request handling). Current revision: views in `core`; domain **Model** lives in `inventory.Device`.

| Layer | Role in this revision |
|-------|------------------------|
| Model | `inventory.Device` (+ Django built-ins) |
| Template | unused |
| View | `core.views.health`, `core.views.version` |

**HttpRequest** carries method, path, query (`QueryDict`), body, headers, `META`, user, session. `/health/` exposes a structured snapshot for development and regression tests.

**JsonResponse** for deterministic JSON; **DRF** follows in CRUD modules.

---

## GET /health/ contract

| Item | Value |
|------|--------|
| Method | GET |
| Path | `/health/` |
| Route name | `health` |
| Status | 200 |
| Header | `X-API-Version: 1.0` |
| Body | `status: ok` plus structured request mirror |

Implementation: `core/views.py` — `health`.

---

## URL routing

`config/urls.py`:

```text
admin/
''          → include("core.urls")
inventory/  → include("inventory.urls")   # reserved; views in D3+
```

`core/urls.py`:

| Path | View | `name` |
|------|------|--------|
| `health/` | `health` | `health` |
| `version/` | `version` | `version` |

**`reverse(name)`** builds URLs; **`resolve(path)`** maps paths back to view callables — covered in `tests/test_routing.py`.

---

## django.test.Client

Runs the full Django stack **in-process** (no listening TCP socket). Contrasts with **httpx** against `runserver`, `live_server`, or Compose.

`tests/test_health.py`: GET, query parameters, repeated keys, `QueryDict` semantics.

---

## Module D1.2 — configuration (12-factor)

`load_dotenv(BASE_DIR / ".env")` in **`config/settings.py`** so WSGI/ASGI see the same env as `manage.py`.

| Variable | Role |
|----------|------|
| `DJANGO_SECRET_KEY` | required |
| `DJANGO_DEBUG` | `1` / `TRUE` → debug on |
| `DJANGO_ALLOWED_HOSTS` | comma-separated hosts |

Template: `.env.example` (committed). Secrets: `.env` (ignored).

---

## Module D1.3 — named routes

| Mechanism | Failure mode |
|-----------|----------------|
| `reverse(name)` | `NoReverseMatch` |
| `resolve(path)` | `Resolver404` |
| `Client.get("/unknown/")` | HTTP **404** |

`GET /version/` → `{"api": "device-inventory", "module": "core"}`.

Tests: `tests/test_routing.py`.

---

## GET /version/ contract

| Item | Value |
|------|--------|
| Path | `/version/` |
| Name | `version` |
| Body | `api`, `module` metadata JSON |

---

## Database configuration (`DB_ENGINE`)

| `DB_ENGINE` | Engine | Typical use |
|-------------|--------|-------------|
| `sqlite` | SQLite | local dev, fast ORM tests |
| `postgresql` | PostgreSQL | S1, locking/isolation labs, production profile |

Required in `.env` (see `.env.example`):

| Variable | Role |
|----------|------|
| `DB_ENGINE` | `sqlite` or `postgresql` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Postgres when `DB_ENGINE=postgresql` |

SQLite options in settings:

- **`transaction_mode: IMMEDIATE`** — concurrency-friendly defaults for teaching;
- **`TEST.NAME`** — separate test database file from dev `db.sqlite3`.

**`psycopg`** v3 is listed in `requirements.txt`.

```bash
python manage.py migrate
python manage.py dbshell
```

---

## Module D2 — ORM and Device model

### Objective

Persist the **device inventory** domain: schema, migrations, ORM, field alignment with **`device_lab`** mock.

### Pydantic vs Django

| Aspect | `device_lab.Device` | `inventory.Device` |
|--------|---------------------|---------------------|
| Role | validate dict → in-memory object | table row + ORM |
| Persistence | none | `save()`, migrations |
| States | `DeviceState` StrEnum | `DeviceStatus` TextChoices (stored as strings) |
| ID | supplied at `register()` | **auto-generated** `device-NNN` in `save()` (API contract clarified in D5B) |

### Model schema

| Field | ORM | Semantics |
|-------|-----|-----------|
| `device_id` | `CharField`, **PK**, `editable=False` | e.g. `device-001` |
| `firmware_version` | default `"1.0.0"` | matches mock |
| `state` | choices | `online`, `offline`, `dfu_in_progress` |
| `last_seen_at` | nullable `DateTimeField` | `None` until heartbeat (D5) |
| `created_at` / `updated_at` | auto timestamps | audit |

**`Meta.ordering`** sorts by numeric suffix (`device-998` … `device-1001`), not raw string order.

**`DeviceQuerySet.ordered_by_device_number()`** is kept for teaching (explicit queryset ordering vs default `Meta.ordering`).

### ID generation in `save()`

Inside **`transaction.atomic()`**:

- **SQLite:** `max(numeric suffix) + 1`, dynamic zero-padding;
- **PostgreSQL:** `DeviceCounter` row pk=1 with **`select_for_update()`**.

Migrations: `0001_initial`, `0002_create_device_counter` (data), `0003_alter_device_options`.

### D2 definition of done

- `inventory` app registered;
- migrations applied;
- state values match `device_lab`;
- `DB_ENGINE` switch + `psycopg` in requirements.

---

## Module T2.1 — ORM testing

File: **`tests/test_device_model.py`**.

| Base class | Use in this repo |
|------------|------------------|
| **TestCase** | defaults, `IntegrityError`, filters, `setUpTestData`, ordering |
| **TransactionTestCase** | threads, `select_for_update`, isolation, savepoints |

`manage.py test` creates a **dedicated test database** and does not corrupt dev `db.sqlite3`.

**Overview**

- **DeviceModelTest / DeviceSharedDataTest** — core D2 acceptance;
- **DeviceConcurrencyTest** — parallel `create()` on SQLite;
- **DeviceIsolationTest**, **SkipLocked**, **Deadlock**, serialization retry — **PostgreSQL only** (`skipTest` when `connection.vendor != "postgresql"`).

On SQLite expect **~65 tests** total with health/routing: OK with **~15 skipped**.

Full regression:

```bash
python manage.py test tests.test_device_model tests.test_routing tests.test_health -v 2
```

Run without skips: set `DB_ENGINE=postgresql` and apply migrations to a real Postgres instance (module S1).

---

## Test commands

| Command | Purpose |
|---------|---------|
| `python manage.py check` | system checks |
| `python manage.py test` | all Django tests |
| `python manage.py test tests.test_device_model tests.test_routing tests.test_health -v 2` | main regression bundle |
| `python manage.py test tests.test_device_model -v 2` | D2/T2 only |

---

## Curriculum status

Sequence: **D0** → **D1/T1** → **D2/T2** → **S1** → **D3–D5B** → **T6** → **D6/T6b**. Details: **[docs/PLAN.en.md](docs/PLAN.en.md)**.

| Module | Artifact |
|--------|----------|
| D0 | bootstrap, docs |
| D1 | `core/`, `/health/` |
| D1.2 | env-driven settings |
| D1.3 | `/version/`, `test_routing` |
| T1 | `test_health` |
| **D2** | `inventory`, `Device`, migrations, `DB_ENGINE` |
| **T2.1** | `test_device_model.py` |

---

## Next steps

| Stage | Content |
|-------|---------|
| S1 | PostgreSQL ops, `docs/SQL.md`, green PG-only tests |
| D3–D5 | DRF, auth, inventory HTTP API |
| D5B | traceability to `device_lab` routes and 409 transitions |
| T6 | httpx + Pydantic + Allure |
| D6/T6b | Compose, GitHub Actions |

---

## References

- https://github.com/ANDRZEJSZAMBORSKI/device_inventory_api  
- https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep  
- https://docs.djangoproject.com/en/5.2/