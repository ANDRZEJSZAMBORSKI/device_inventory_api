# Curriculum: Device Inventory API

**EN** · [RU](PLAN.md) · [PL](PLAN.pl.md)

**Version:** 2026-11-11  
**Case repository:** https://github.com/ANDRZEJSZAMBORSKI/device_inventory_api  
**Prerequisite lab:** https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep (`device_lab`)

---

## 1. Program objectives

Develop a complete Django web service lifecycle:

- HTTP API and routing design;
- schema design and migrations;
- PostgreSQL administration and SQL ↔ ORM mapping;
- DRF REST with authentication and authorization;
- layered testing (in-process and black-box HTTP);
- delivery via Docker Compose and GitHub Actions.

Domain: **device inventory** (online/offline, heartbeat, DFU), traceable to the `device_lab` mock specification.

---

## 2. Learning outcomes

| ID | Outcome |
|----|---------|
| LO-1 | Explain MTV, Django request lifecycle, middleware |
| LO-2 | Design modular urlconf with `include` and named routes |
| LO-3 | Implement views and JSON responses; justify DRF adoption |
| LO-4 | Design models, migrations, ORM and SQL equivalents |
| LO-5 | Test views with `Client`; test APIs with `APITestCase` |
| LO-6 | Deliver REST CRUD, auth, filters, error contracts |
| LO-7 | Automate device state flows (heartbeat, DFU) |
| LO-8 | Integrate httpx + Pydantic + Allure against deployed service |
| LO-9 | Build images, Compose stacks, CI pipelines with test artifacts |

---

## 3. Prerequisites

Python 3.11+, virtual environments, Git, HTTP/JSON, SQL basics, pytest and HTTP client experience (hp-qa-junior-prep).

---

## 4. Program structure

| Block | Modules | Topics |
|-------|---------|--------|
| **I** | D0, D1, T1 | Tooling, HTTP, Client tests |
| **II** | D2, T2, S1 | ORM, pytest-django, PostgreSQL |
| **III** | D3–D5B, T3–T5 | DRF, auth, Inventory domain |
| **IV** | T6 | httpx, Pydantic, Allure |
| **V** | D6, T6b | Docker Compose, GitHub Actions |

Estimated workload: 200–280 hours of guided implementation and documentation.

---

## 5. Block I — HTTP and tooling

### D0 — Project bootstrap

venv, dependencies, `startproject`, migrations for built-in apps, VCS, tri-lingual docs. **Status: implemented.**

### D1 — HTTP layer

MTV, `HttpRequest`, `JsonResponse`, nested urlconf. Lab: `core` app, `/health/` diagnostic JSON (`status: ok` + request mirror). **Status: implemented** (`core/views.py`, `core/urls.py`, `config/urls.py`).

### T1 — View-level testing

`TestCase`, `Client`, test database, `QueryDict` semantics. Lab: `tests/test_health.py`. **Status: implemented.**

### D1.2 — Configuration (next)

`python-dotenv`, secrets, `ALLOWED_HOSTS`.

---

## 6. Block II — Data

D2 Device model; T2 model tests + pytest-django; S1 PostgreSQL + `docs/SQL.md`.

---

## 7. Block III — REST

D3/T3 DRF CRUD; D4/T4 auth and isolation; D5/T5 API hardening; D5B traceability to `device_lab`.

---

## 8. Block IV — External automation

T6 httpx, Pydantic schemas, Allure reports.

---

## 9. Block V — Delivery

D6 Dockerfile and Compose (web, db, migrate, test job); T6b GitHub Actions + Allure artifacts.

---

## 10. Deliverables matrix

| Artifact | Module |
|----------|--------|
| `README*.md` | D0+, updated per block |
| `docs/API.md` | D5 |
| `docs/SQL.md` | S1 |
| `docker-compose.yml` | D6 |
| `.github/workflows/` | T6b |

---

## 11. Pedagogy

Git commits per module; documentation in RU/EN/PL; regression via `manage.py test` → pytest → CI.

---

## 12. Target architecture

Client → WSGI → middleware → DRF → ORM → PostgreSQL; CI runs Compose + tests + Allure.

---

## 13. References

Django 5.2, DRF, PostgreSQL docs, OWASP API Security (auth module).

---

## 14. Repository timeline

| Revision | Content |
|----------|---------|
| bootstrap | D0 |
| http-d1 | D1/T1 `core`, `/health/`, tests |
| config-d1.2 | dotenv, env `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` |
| planned | D1.3+, D2 models |
