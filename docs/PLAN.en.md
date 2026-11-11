# Learning plan: Device Inventory API

**EN** · [RU](PLAN.md) · [PL](PLAN.pl.md)

**Updated:** 2026-11-11  
**Repo:** `device_inventory_api`  
**Continuation of:** [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep) — mock `device_lab` → **real** Django backend.

---

## 1. Purpose

One end-to-end **portfolio backend** covering the **full program**:

| Layer | Topics |
|-------|--------|
| **Django** | MTV, settings, URLs, templates as needed, admin (brief) |
| **Database** | SQLite (D1–D2) → **PostgreSQL** (S1), ORM, migrations, SQL |
| **API** | DRF: serializers, ViewSets, auth, validation, filters |
| **Domain** | Device inventory: states, heartbeat, DFU — same as `device_lab` |
| **Testing** | `TestCase` + `Client`, `APITestCase`, **pytest-django**, DB asserts |
| **QA automation** | **httpx** + **Pydantic** + **Allure** (lab_fw ideas, against live Django) |
| **Infra** | **Dockerfile**, **Docker Compose** (web + postgres + tests), **GitHub Actions** |

**Mode:** spec → you code → theory → review. No changes to your logic/tests without OK.

---

## 2. Progress

| Module | Status |
|--------|--------|
| **D0** bootstrap | nearly done: add **git** + tri-lingual docs |
| **D1.1 + T1.1** | **next** — health + Client |
| Block A rest | open |
| Blocks B–D | locked until A passed |

Put Django/DRF on resume only after **block A** (your call).

---

## 3. Mandatory sequence

```text
Block A — Django core
  D0  venv, startproject, git
  D1  MTV, URLs, JsonResponse (no DRF)
  T1  TestCase + Client
  D2  Device model, ORM
  T2  model tests + pytest-django
  S1  PostgreSQL + docs/SQL.md

Block B — API & domain
  D3  DRF CRUD
  T3  APITestCase
  D4  Auth + owner
  T4  401/403
  D5  filters, errors, docs/API.md
  T5  CRUD matrix, DB asserts
  D5B  heartbeat + DFU (device_lab parity)
  T5+  transitions, 409

Block C — external QA layer
  T6  httpx + Pydantic + Allure

Block D — containers & CI
  D6  Docker + Compose
  T6b  GitHub Actions + Allure artifact
```

Ship **D + T** together; no skipping.

---

## 4. Module details (summary)

- **D0:** venv, Django 5.x, `check`, migrate, `.gitignore`, tri-lingual README/PLAN, git.
- **D1/T1:** health endpoint, Client tests, dotenv in D1.2.
- **D2/T2:** Device model, migrations, pytest-django.
- **S1:** Postgres, SQL exercises.
- **D3/T3:** DRF CRUD, ≥10 APITests.
- **D4/T4:** Token or JWT, ownership isolation.
- **D5/T5:** production-style API, ≥40 API tests total toward end of B.
- **D5B:** heartbeat/DFU routes aligned with `hp-qa` mock API.
- **T6:** black-box httpx tests, Allure.
- **D6/T6b:** Compose (web+db+test job), GHA on PR, Allure upload.

---

## 5. Target repo layout

`config/`, `apps/`, `tests/{unit,api,integration}/`, `docs/`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/`.

---

## 6. End-of-track DoD

Explain and demonstrate: ORM/migrations, test layers, HTTP+Postgres checks, DRF errors, Compose green run, green CI.

---

## 7. Module sign-off

Code in git, command output, theory answers, review (you fix).

---

## 8. Time (~8–12 h/week)

A: 2–3 weeks · B: 4–6 · C–D: 2–3.

---

## 9. Out of scope (for now)

Celery, Kafka, K8s prod, GraphQL.

---

## 10. Next step

Finish **D0** (git + docs commit) → **D1.1 + T1.1**.
