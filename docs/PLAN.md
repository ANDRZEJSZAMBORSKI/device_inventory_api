# Учебная программа курса: Device Inventory API

**RU** · [EN](PLAN.en.md) · [PL](PLAN.pl.md)

**Версия:** 2026-11-11  
**Репозиторий-кейс:** https://github.com/ANDRZEJSZAMBORSKI/device_inventory_api  
**Предшествующий практикум:** https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep (`device_lab`)

---

## 1. Цели программы

По завершении программы участник владеет полным циклом разработки веб-сервиса на Django:

- проектирование HTTP API и маршрутизации;
- проектирование схемы данных и миграций;
- администрирование PostgreSQL и сопоставление SQL ↔ ORM;
- реализация REST с DRF, аутентификацией и разграничением доступа;
- многоуровневым тестированием (in-process и black-box HTTP);
- поставкой через Docker Compose и GitHub Actions.

Доменная область: **инвентаризация устройств** (online/offline, heartbeat, DFU) — согласована с mock-реализацией `device_lab` для сквозной трассируемости требований.

---

## 2. Результаты обучения (компетенции)

| Код | Компетенция |
|-----|-------------|
| LO-1 | Объяснять MTV, жизненный цикл HTTP-запроса в Django, роль middleware |
| LO-2 | Проектировать urlconf с `include`, именованные маршруты, reverse |
| LO-3 | Писать функциональные views и JSON-ответы; обосновать выбор DRF |
| LO-4 | Проектировать модели, миграции, выполнять ORM-операции и SQL-эквиваленты |
| LO-5 | Тестировать views через `Client`; тестировать API через `APITestCase` |
| LO-6 | Реализовать REST CRUD, auth, фильтры, коды ошибок |
| LO-7 | Автоматизировать сценарии состояний устройств (heartbeat, DFU) |
| LO-8 | Интегрировать httpx + Pydantic + Allure против развёрнутого сервиса |
| LO-9 | Собирать образы, Compose-стек, pipeline CI с артефактами тестов |

---

## 3. Предварительные требования

- Python 3.11+, виртуальные окружения, Git.
- HTTP, JSON, основы SQL.
- Практика pytest и HTTP-клиентов (из hp-qa-junior-prep).

---

## 4. Структура программы

| Блок | Модули | Содержание |
|------|--------|------------|
| **I** | D0, D1, T1 | Инфраструктура, HTTP, Client-тесты |
| **II** | D2, T2, S1 | ORM, pytest-django, PostgreSQL |
| **III** | D3–D5B, T3–T5 | DRF, auth, домен Inventory |
| **IV** | T6 | httpx, Pydantic, Allure |
| **V** | D6, T6b | Docker Compose, GitHub Actions |

Ориентировочная трудоёмкость: 200–280 часов самостоятельной работы с кодовой базой и документацией.

---

## 5. Модуль I — HTTP и инфраструктура

### Модуль D0 — Среда и каркас проекта

**Темы:** venv, зависимости, `startproject`, `manage.py`, миграции встроенных apps, VCS.

**Артефакты:** `config/`, `requirements.txt`, `.gitignore`, `.env.example`, документация RU/EN/PL.

**Реализовано в репозитории:** да.

### Модуль D1 — HTTP-слой Django

**Темы:** MTV; `HttpRequest`; `JsonResponse`; составные urlconf; заголовки ответа.

**Практикум:** приложение `core`, маршрут `health/`, view `health` — диагностический JSON эндпоинт с полем `status: ok` и структурированным отражением параметров запроса.

**Точки в коде:** `core/views.py`, `core/urls.py`, `config/urls.py`, `config/settings.py` (`INSTALLED_APPS`).

**Реализовано в репозитории:** да.

### Модуль D1.3 — Именованные маршруты

**Темы:** `name=` в `path`, `reverse`, `resolve`, HTTP 404 vs `NoReverseMatch` / `Resolver404`.

**Практикум:** `version/`; `tests/test_routing.py`. **Реализовано:** да.

### Модуль T1 — Тестирование уровня View

**Темы:** `django.test.TestCase`, `Client`, тестовая БД; contrast с httpx; `QueryDict`.

**Практикум:** `tests/test_health.py` — регрессия эндпоинта и семантики query-параметров.

**Реализовано в репозитории:** да.

### Модуль D1.2 — Конфигурация

`python-dotenv`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, разделение dev/prod настроек. **Реализовано:** `config/settings.py`, `.env.example`.

---

## 6. Модуль II — Данные

### D2 — ORM и доменная модель Device

Поля: идентификатор устройства, версия прошивки, состояние, `last_seen_at`, аудит. Миграции, ограничения уникальности, admin (опционально).

### T2 — Тесты модели

`TestCase`, `setUpTestData`, `pytest-django`, `@pytest.mark.django_db`, `IntegrityError`.

### S1 — PostgreSQL

Переключение `DATABASES`, документ `docs/SQL.md`: SELECT/JOIN/GROUP BY, пары с ORM, транзакции.

---

## 7. Модуль III — REST API

### D3 / T3 — DRF fundamentals

Serializers, ViewSet, router, pagination, validation 400, ≥10 APITestCase без auth.

### D4 / T4 — Безопасность

Register, token auth (или JWT), `IsAuthenticated`, owner FK, queryset filtering, матрица 401/403.

### D5 / T5 — Inventory API

Фильтры, единый формат ошибок, `docs/API.md`, asserts в БД после HTTP, E2E DFU.

### D5B — Согласованность с device_lab

Таблица трассировки mock-маршрутов → DRF endpoints; коды 409 при недопустимых переходах.

---

## 8. Модуль IV — Внешняя автоматизация

### T6

`live_server` или URL Compose; httpx; Pydantic-схемы ответов; Allure; сравнение дублирования с APITestCase.

---

## 9. Модуль V — Поставка

### D6 — Контейнеризация

Dockerfile, Compose: `web`, `db`, one-shot `migrate`, сервис `tests`, healthcheck PostgreSQL, volumes.

### T6b — CI/CD

GitHub Actions: установка deps, БД, `migrate`, `pytest`, артефакт Allure, статусный badge.

---

## 10. Матрица артефактов программы

| Артефакт | Модуль появления |
|----------|------------------|
| `README*.md` | D0, обновление после каждого блока |
| `docs/PLAN*.md` | D0 |
| `docs/API.md` | D5 |
| `docs/SQL.md` | S1 |
| `docker-compose.yml` | D6 |
| `.github/workflows/*.yml` | T6b |
| Отчёты Allure | T6 |

---

## 11. Методика

- Каждый модуль завершается фиксацией в Git и обновлением документации на трёх языках.
- Теория фиксируется в README (разделы курса) и в конспектах участника.
- Регрессия: `python manage.py test`, далее pytest, далее CI.

---

## 12. Справочная архитектура (целевая)

```text
[Client] → [Gunicorn/WSGI] → [Django middleware]
         → [DRF ViewSets] → [ORM] → [PostgreSQL]
[CI/GHA] → [Compose] → pytest + httpx → Allure artifact
```

---

## 13. Литература и стандарты

- Django Documentation 5.2 — https://docs.djangoproject.com/en/5.2/
- Django REST Framework — https://www.django-rest-framework.org/
- PostgreSQL Documentation — https://www.postgresql.org/docs/
- OWASP API Security — ориентир для auth-модуля

---

## 14. Хронология репозитория

| Ревизия | Содержание |
|---------|------------|
| bootstrap | D0: Django project `config`, зависимости |
| http-d1 | D1/T1: `core`, `/health/`, `tests/test_health.py` |
| config-d1.2 | `load_dotenv`, env-driven `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` |
| routing-d1.3 | `version`, `reverse`/`resolve`, `test_routing` |
| *planned* | D2 models, … |

---

## 15. Связанные репозитории

- **hp-qa-junior-prep** — mock API, httpx, Compose, GHA, Allure; перенос паттернов в модуль T6.
- **local-sqlite-manager** — SQL и тестовая дисциплина (косвенный фундамент).
