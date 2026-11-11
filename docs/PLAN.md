# План обучения: Device Inventory API

**RU** · [EN](PLAN.en.md) · [PL](PLAN.pl.md)

**Обновлено:** 2026-11-11  
**Репозиторий:** `device_inventory_api`  
**Продолжение:** [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep) — mock `device_lab` → **реальный** Django backend.

---

## 1. Зачем этот проект

Один сквозной **portfolio backend**, где проходим **полную программу**:

| Слой | Содержание |
|------|------------|
| **Django** | MTV, settings, URLs, templates (по мере надобности), admin (кратко) |
| **БД** | SQLite (D1–D2) → **PostgreSQL** (S1), ORM, migrations, SQL |
| **API** | DRF: serializers, ViewSets, auth, валидация, фильтры |
| **Домен** | Device inventory: states, heartbeat, DFU — как в `device_lab` |
| **Тесты** | `TestCase` + `Client`, `APITestCase`, **pytest-django**, asserts в БД |
| **QA automation** | **httpx** + **Pydantic** + **Allure** (как в lab_fw, но против живого Django) |
| **Инфра** | **Dockerfile**, **Docker Compose** (web + postgres + tests), **GitHub Actions** |

**Режим:** ТЗ → ты кодируешь → теория → review. Логику и тесты ассистент не меняет без твоего OK.

**Не смешиваем без запроса:** NeetCode 2nd pass, mock interview, правки в `hp-qa-junior-prep`.

---

## 2. Текущий прогресс

| Модуль | Статус |
|--------|--------|
| **D0** bootstrap | почти готов: venv, Django 5.2, `check`, migrate, `.env.example` — добавить **git** + README/PLAN |
| **D1.1 + T1.1** | **следующая лаба** — health + Client |
| Блок A остальное | открыто |
| Блок B–D | locked до сдачи A |

**Резюме:** Django/DRF в skills — только после **блока A** (твоё решение).

---

## 3. Обязательная последовательность

```text
Блок A — Django core
  D0  venv, startproject, git, manage.py check
  D1  MTV, URLs, JsonResponse (без DRF)
  T1  django.test.TestCase + Client
  D2  Models Device, migrations, ORM
  T2  тесты моделей + pytest-django
  S1  PostgreSQL + docs/SQL.md

Блок B — API и домен
  D3  DRF, CRUD /api/devices/
  T3  APITestCase
  D4  Auth (Token или SimpleJWT — один путь), owner
  T4  401/403, изоляция users
  D5  validation, filters, errors, docs/API.md
  T5  CRUD matrix, assert в БД, DFU E2E
  D5B  heartbeat + DFU (паритет device_lab)
  T5+  тесты переходов, 409

Блок C — внешний QA-слой
  T6  httpx + live_server/Compose + Pydantic + Allure

Блок D — контейнеры и CI
  D6  Dockerfile + Compose (web, db, migrate, test service)
  T6b  GitHub Actions: postgres service или compose, pytest, Allure artifact
```

**Правило:** сдаём **D + T** парой; без ✅ следующий модуль не открываем.

---

## 4. Детализация модулей

### D0 — Bootstrap

| ID | Практика | DoD |
|----|----------|-----|
| D0.1 | venv, Django 5.x, `startproject config .` | `check` 0 issues |
| D0.2 | migrate (sqlite), `.gitignore`, `requirements.txt` | `db.sqlite3` не в git |
| D0.3 | `.env.example`, README RU/EN/PL, `docs/PLAN.*` | документация |
| D0.4 | `git init`, commit, (опц.) push GitHub | чистый `git status` |

### D1 — Django без DRF

| ID | Практика |
|----|----------|
| D1.1 | `startapp`, `GET /health/` → `JsonResponse({"status": "ok"})` |
| D1.2 | `load_dotenv`, `SECRET_KEY` из `.env`, `DEBUG`, `ALLOWED_HOSTS` |
| D1.3 | `include()` app urls, named URL `health` |

### T1 — Client

| ID | Практика |
|----|----------|
| T1.1–T1.3 | `test_health`, 404, зачаток `pytest --ds=config.settings` |

### D2 — Models + ORM

`Device`: `device_id`, `firmware_version`, `state` (choices), `last_seen_at`, timestamps. Migrations, shell CRUD.

### T2 — pytest-django

TestCase + `@pytest.mark.django_db`, unique constraint, (опц.) num_queries.

### S1 — PostgreSQL

`DATABASES` → Postgres, `docs/SQL.md` (7+ запросов, пары SQL ↔ ORM).

### D3 — DRF

ModelSerializer, ViewSet, router, pagination, validation 400.

### T3 — APITestCase

≥10 тестов CRUD без auth.

### D4 — Auth

Register, Token **или** JWT, `IsAuthenticated`, owner FK.

### T4 — Auth tests

401 anonymous, два user — нет утечки данных.

### D5 — Inventory API

Фильтры, единый формат ошибок, `docs/API.md`, (опц.) OpenAPI.

### D5B — Паритет `device_lab`

| Mock (`hp-qa`) | Django (цель) |
|----------------|---------------|
| `GET /devices` | `GET /api/devices/` |
| `POST .../heartbeat` | online + `last_seen_at` |
| DFU start/complete/fail | state machine + 409 |

### T5 — Глубокие API-тесты

≥40 API-тестов суммарно; POST → `Device.objects.get()`; DFU сценарий.

### T6 — httpx + Allure

`live_server`, Pydantic response models, Allure steps, README как смотреть отчёт.

### D6 — Docker Compose

Сервисы: **web** (gunicorn/runserver prod-like), **db** (postgres), **migrate** one-shot, **tests** (pytest). Healthcheck db, volumes.

### T6b — GitHub Actions

Workflow на PR: установка зависимостей, Postgres (service или compose), `migrate`, `pytest`, upload Allure `if: always()`, badge в README.

---

## 5. Целевая структура репозитория

```text
device_inventory_api/
  config/
  apps/accounts/, apps/devices/
  tests/unit/, tests/api/, tests/integration/
  docs/PLAN.*, API.md, SQL.md
  Dockerfile
  docker-compose.yml
  .github/workflows/ci.yml
  README.md, README.en.md, README.pl.md
```

---

## 6. Definition of Done (весь трек)

Ты можешь **объяснить и показать**:

1. Project / app / migrations / ORM.  
2. Разницу **TestCase** vs **APITestCase** vs **pytest-django** vs **httpx**.  
3. Проверку **HTTP + строка в Postgres**.  
4. DRF validation и коды ошибок.  
5. `docker compose up` → тесты green.  
6. CI на GitHub зелёный на PR.

---

## 7. Критерий сдачи модуля

1. Код в git.  
2. Вывод команд.  
3. 3–7 теоретических ответов.  
4. Review — правки делаешь ты.

---

## 8. Ориентир по времени (~8–12 ч/нед)

| Блок | Недели |
|------|--------|
| A (D0–S1) | 2–3 |
| B (D3–D5B) | 4–6 |
| C–D (T6, D6, T6b) | 2–3 |

---

## 9. Вне scope (пока)

Celery, Kafka, K8s production, GraphQL, enterprise JWT rotation.

---

## 10. Следующий шаг

Закрыть **D0** (git + коммит документации) → **D1.1 + T1.1**.
