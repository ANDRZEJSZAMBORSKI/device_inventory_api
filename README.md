# Device Inventory API

**RU** · [EN](README.en.md) · [PL](README.pl.md)

<!-- readme-preamble -->

**Device Inventory API** — портфолио-проект на **Django**: backend, база данных, REST API, тестирование в экосистеме Django, затем **Docker / Docker Compose** и **GitHub Actions**. Это **продолжение** учебного репозитория [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep): там — mock **Device Inventory** (`device_lab`, HTTP-моки, pytest, Allure, CI); **здесь** — **реальный** сервис на Django/DRF + **PostgreSQL**, с тем же доменом (устройства, heartbeat, DFU, состояния online/offline).

| Версия трека | Статус на 2026-11-11 |
|--------------|----------------------|
| **D0** — bootstrap (venv, `startproject`, git) | в работе |
| **D1–D6, T1–T6, S1, T6b** | по [docs/PLAN.md](docs/PLAN.md) |

Полная программа: Django **без** DRF → models/ORM → Postgres/SQL → DRF → auth → Inventory API → pytest-django / APITestCase → **httpx** + Pydantic + Allure → **контейнеры + GHA**.

### Для кого

- Junior **Python / Backend / QA**, который прошёл API-автоматизацию в `hp-qa-junior-prep` и собирает **полноценный backend** под резюме.
- Тот, кто хочет честно связать **mock → production-style API** на одном домене.

### Связь с hp-qa-junior-prep

| hp-qa-junior-prep | device_inventory_api |
|-------------------|----------------------|
| `src/device_lab/` — in-memory + `MockTransport` | Django models + Postgres |
| `tests/device_lab/` (~76 тестов) | `tests/` — Django TestCase, APITestCase, pytest-django, позже httpx |
| Compose + MockServer + GHA | Compose **web + db + test job** + GHA на этом репо |
| Pydantic `Device`, state machine | DRF serializers + те же переходы (D5B) |

### Требования

| Компонент | Примечание |
|-----------|------------|
| Python | **≥ 3.11** (сейчас venv может быть 3.14 — ок для учёбы) |
| Git | обязателен с D0 |
| Docker Desktop | блок **D6** (Compose) |
| PostgreSQL | блок **S1** (локально или в контейнере) |

### Документация

| Файл | Язык |
|------|------|
| [docs/PLAN.md](docs/PLAN.md) | RU — полный план модулей D/T/S |
| [docs/PLAN.en.md](docs/PLAN.en.md) | EN |
| [docs/PLAN.pl.md](docs/PLAN.pl.md) | PL |

### Быстрый старт (текущий этап D0)

```bash
cd /d/pyton_2/git/device_inventory_api
source .venv/Scripts/activate

python manage.py check
python manage.py migrate
python manage.py runserver
```

Открой `http://127.0.0.1:8000/` — стартовая страница Django. Секреты: скопируй `.env.example` → `.env` (подключение `dotenv` в **D1.2**).

### Структура (целевая; нарастает по модулям)

```text
device_inventory_api/
  config/              # settings, urls, wsgi
  apps/
    devices/           # D2+
    accounts/          # D4
  tests/               # T1+
  docs/                # PLAN, API.md, SQL.md
  docker-compose.yml   # D6
  .github/workflows/   # T6b
```

Сейчас: `config/`, `manage.py`, `requirements.txt`.

### Что будет в конце трека (Definition of Done)

- REST API устройств + auth + heartbeat/DFU (паритет с `device_lab`).
- **PostgreSQL** + примеры SQL в `docs/SQL.md`.
- Тесты: **Client**, **APITestCase**, **pytest-django**, слой **httpx** + Allure.
- **Docker Compose**: приложение + БД + прогон тестов.
- **GitHub Actions**: migrate → pytest → артефакт Allure.

### Режим обучения

ТЗ → ты пишешь код и тесты → теория → review. Логику проекта и тестов ассистент **не меняет** без твоего явного OK (как в `hp-qa-junior-prep`).

### Лицензия

Учебный / portfolio-проект. Детали — по мере появления `LICENSE`.
