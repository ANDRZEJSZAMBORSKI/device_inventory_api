# Device Inventory API

**RU** · [EN](README.en.md) · [PL](README.pl.md)

<!-- readme-preamble -->

**Device Inventory API** — учебно-производственный репозиторий полного цикла разработки веб-сервиса на **Django**: HTTP-слой, персистентность (SQLite → PostgreSQL), **Django REST Framework**, доменная модель инвентаризации устройств, автоматизированное тестирование, контейнеризация и непрерывная интеграция. Проект логически продолжает [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep): mock-слой `device_lab` здесь реализуется как **реальный backend** с той же предметной областью (состояния устройств, heartbeat, обновление прошивки).

Документ одновременно **эксплуатационная инструкция** (команды, структура, тесты) и **учебное пособие по архитектуре Django** с привязкой к исходному коду. Три языка: **RU** (этот файл), [EN](README.en.md), [PL](README.pl.md). Детальный учебный план курса: [docs/PLAN.md](docs/PLAN.md).

### Назначение системы

| Компонент | Роль |
|-----------|------|
| **Django (MTV)** | Маршрутизация HTTP, views, ORM, административный слой |
| **PostgreSQL** | Производственное хранилище после модуля персистентности |
| **DRF** | REST API, сериализация, аутентификация, пагинация |
| **Тестовый контур** | `django.test.Client`, `APITestCase`, `pytest-django`, внешний **httpx** |
| **Инфраструктура** | Docker Compose (приложение + БД), GitHub Actions |

### Связь с hp-qa-junior-prep

| Mock / automation (hp-qa) | Backend (этот репозиторий) |
|---------------------------|----------------------------|
| `InMemoryInventory`, `MockTransport` | ORM + транзакции Postgres |
| Pydantic `Device`, FSM состояний | DRF serializers + бизнес-правила |
| `tests/device_lab/` | `tests/api/`, интеграционный слой httpx |
| Compose, MockServer, GHA | Compose web+db, workflow pytest |

### Требования к окружению

| Компонент | Версия / примечание |
|-----------|---------------------|
| Python | ≥ 3.11 |
| Django | 5.2.x (см. `requirements.txt`) |
| Git | история изменений и CI |
| Docker Desktop | модуль контейнеризации (поздний этап) |
| PostgreSQL | модуль SQL/ORM (контейнер или локальный инстанс) |

### Карта документации

| Раздел README | Содержание | Код |
|---------------|------------|-----|
| [Быстрый старт](#быстрый-старт) | venv, check, migrate, runserver, тесты | корень репозитория |
| [Структура](#структура-репозитория) | пакеты `config`, `core`, каталог `tests` | — |
| [Модуль D1 — HTTP и MTV](#модуль-d1--http-слой-и-mtv) | `HttpRequest`, `JsonResponse`, маршруты | `core/views.py`, `core/urls.py` |
| [Эндпоинт /health/](#контракт-get-health) | диагностический JSON | `core/views.py` |
| [Тестирование Client](#тестирование-djangotestclient) | in-process HTTP без сокета | `tests/test_health.py` |
| [Модуль D1.2 — конфигурация](#модуль-d12--конфигурация-и-12-factor) | `.env`, секреты, `ALLOWED_HOSTS` | `config/settings.py` |
| [Учебный план](#учебная-программа) | полная программа курса | `docs/PLAN.md` |

### Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Структура репозитория](#структура-репозитория)
3. [Модуль D1 — HTTP-слой и MTV](#модуль-d1--http-слой-и-mtv)
4. [Контракт GET /health/](#контракт-get-health)
5. [Маршрутизация URL](#маршрутизация-url)
6. [Тестирование django.test.Client](#тестирование-djangotestclient)
7. [Модуль D1.2 — конфигурация и 12-factor](#модуль-d12--конфигурация-и-12-factor)
8. [Команды тестирования](#команды-тестирования)
9. [Учебная программа](#учебная-программа)
10. [Дальнейшее развитие](#дальнейшее-развитие)

---

## Быстрый старт

```bash
cd /d/pyton_2/git/device_inventory_api
source .venv/Scripts/activate
pip install -r requirements.txt

cp .env.example .env
# Заполните DJANGO_SECRET_KEY (см. раздел «Конфигурация»)

python manage.py check
python manage.py migrate
python manage.py runserver
```

Проверка API:

```bash
curl -s http://127.0.0.1:8000/health/ | head
```

Запуск модульных тестов HTTP-слоя:

```bash
python manage.py test tests.test_health -v 2
```

Без файла `.env` и `DJANGO_SECRET_KEY` проект **не стартует** (`ValueError` в `settings.py`) — намеренная защита от запуска без секретов.

---

## Структура репозитория

```text
device_inventory_api/
  config/                 # настройки проекта, корневой urlconf, WSGI/ASGI
  core/                   # приложение: views, urlconf приложения
  tests/                  # проектные тесты (вне startapp)
    __init__.py
    test_health.py        # модуль D1: Client + HttpRequest
  .env.example            # шаблон env (копия → .env локально)
  docs/
    PLAN.md               # учебная программа (RU/EN/PL)
  manage.py
  requirements.txt
  README.md
```

Пакет **`config`** — точка конфигурации Django (`settings`, `urls`, `wsgi`, `asgi`). Пакет **`core`** — первая прикладная app с HTTP views. Каталог **`tests`** — единая точка регрессии на уровне проекта.

---

## Модуль D1 — HTTP-слой и MTV

### Архитектура MTV

**MTV** (Model – Template – View) — организационная модель Django:

| Слой | Ответственность | В текущей ревизии |
|------|-----------------|-------------------|
| **Model** | Схема данных, ORM, бизнес-инварианты у данных | встроенные apps (`auth`, …); доменная модель Device — следующий модуль |
| **Template** | Представление (HTML и др.) | не используется |
| **View** | Обработка `HttpRequest`, выбор ответа | `core.views.health` |

Поток обработки GET `/health/`:

```mermaid
sequenceDiagram
  participant C as Client / TestClient
  participant U as URL resolver
  participant M as Middleware chain
  participant V as health view
  participant R as JsonResponse

  C->>M: HTTP GET /health/
  M->>U: resolve path
  U->>V: views.health(request)
  V->>R: JSON body
  R->>C: HttpResponse
```

### HttpRequest

View получает объект **`HttpRequest`**: метод, путь, `GET`/`POST` (`QueryDict`), тело, заголовки, `META`, пользователь, сессия. Диагностический эндпоинт `/health/` сериализует срез этих атрибутов в JSON для наблюдаемости при разработке и в тестах.

### JsonResponse vs DRF

**`JsonResponse`** достаточен для детерминированного JSON и учебной диагностики. **Django REST Framework** подключается на этапе CRUD API: serializers, validation, auth, browsable API, routers.

---

## Контракт GET /health/

| Элемент | Значение |
|---------|----------|
| Метод | `GET` |
| Путь | `/health/` |
| Имя маршрута | `health` (`reverse("health")`) |
| Статус | `200` |
| Content-Type | `application/json` |
| Заголовок ответа | `X-API-Version: 1.0` |
| Тело | JSON: поле `status: "ok"` + структурированное отражение `request`, `GET`, `POST`, `headers`, `META`, `user`, `session`, … |

Повторяющиеся query-параметры отражаются списками в `GET` (семантика `QueryDict.getlist`). Эндпоинт предназначен для **среды разработки и тестов**; в production health обычно минимизируют до `{"status":"ok"}` без раскрытия метаданных запроса.

Пример (сокращённо):

```json
{
    "status": "ok",
    "request": {
        "method": "GET",
        "path": "/health/",
        "path_info": "/health/",
        "scheme": "http"
    },
    "GET": {},
    "user": {
        "is_authenticated": false,
        "is_anonymous": true
    }
}
```

Реализация: `core/views.py`, функция `health`.

---

## Маршрутизация URL

**Корень** (`config/urls.py`):

```text
admin/  → django.contrib.admin
''      → include("core.urls")
```

**Приложение** (`core/urls.py`):

```text
health/ → views.health (name="health")
```

`include()` делегирует разбор остатка пути дочернему `urlpatterns`, сохраняя модульность: каждое приложение владеет своими маршрутами. Префикс `api/` в будущем вынесет REST под единый namespace без изменения views внутри apps.

---

## Тестирование django.test.Client

**`django.test.Client`** выполняет полный внутренний цикл Django (middleware, resolver, view) **без** TCP-сервера. Это не mock view: вызывается тот же код, что и под WSGI.

| Критерий | `django.test.Client` | `httpx` (внешний клиент) |
|----------|----------------------|---------------------------|
| Транспорт | in-process WSGI | HTTP по сети |
| Сервер | не нужен | `runserver` / `live_server` / Compose |
| Типичное применение | unit/integration view layer | контрактное и E2E тестирование |
| Middleware | да | да (через реальный сервер) |

Файл **`tests/test_health.py`** проверяет:

- базовый GET без query string;
- query-параметры и повторяющиеся ключи;
- поведение `QueryDict` (`get`, `getlist`, immutability, `copy`, `mutable=True`);
- заголовки ответа и структуру JSON.

Запуск:

```bash
python manage.py test tests.test_health
```

Тестовая БД создаётся автоматически (`TestCase`); для текущих тестов персистентность не задействована, но механизм изоляции уже активен.

---

## Модуль D1.2 — конфигурация и 12-factor

### Принцип III (Config)

Конфигурация **отделена от кода**: одни и те же артефакты Git работают в development, test и production; различаются только значения окружения. Секреты и флаги среды **не коммитятся**.

### Загрузка переменных

В `config/settings.py` сразу после `BASE_DIR`:

```python
load_dotenv(BASE_DIR / ".env")
```

Явный путь к файлу в корне репозитория исключает неоднозначность рабочей директории. Точка загрузки — **settings**, а не `manage.py`, потому что приложение поднимается также через **WSGI/ASGI** (Gunicorn, Uvicorn). Если `.env` отсутствует, `load_dotenv` не падает, но без `DJANGO_SECRET_KEY` инициализация останавливается на `ValueError`.

### Переменные окружения

| Переменная | Назначение | Пример |
|------------|------------|--------|
| `DJANGO_SECRET_KEY` | подпись сессий, CSRF, криптография Django | длинная случайная строка |
| `DJANGO_DEBUG` | отладка: `1` или `TRUE` → `DEBUG=True`, иначе `False` | `1` (локально), `0` (prod) |
| `DJANGO_ALLOWED_HOSTS` | разрешённые значения HTTP-заголовка `Host` (без схемы и порта) | `127.0.0.1,localhost` |

Шаблон: **`.env.example`** (в git). Локальные значения: **`.env`** (в `.gitignore`).

Генерация ключа:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### `DEBUG` и `ALLOWED_HOSTS`

При **`DEBUG=True`** Django может показать диагностическую страницу с traceback и контекстом запроса — недопустимо в production. **`ALLOWED_HOSTS`** ограничивает поддельные `Host` (в т.ч. при проксировании через nginx); для `runserver` на `127.0.0.1:8000` в списке достаточно `127.0.0.1`.

### Реализация в коде

- `SECRET_KEY` — обязателен, иначе `raise ValueError`.
- `DEBUG` — явная проверка строки (`1` / `TRUE`).
- `ALLOWED_HOSTS` — split по запятой с `strip`; пустое значение → `[]`.

Файл: `config/settings.py`.

### CI (перспектива)

В GitHub Actions те же имена переменных задаются через **secrets / workflow env**, без файла `.env` в репозитории (модуль T6b).

---

## Команды тестирования

| Команда | Назначение |
|---------|------------|
| `python manage.py check` | системные проверки конфигурации |
| `python manage.py test` | весь набор Django-test |
| `python manage.py test tests.test_health -v 2` | модуль D1 |
| `python manage.py show_urls` | *(при установке django-extensions)* обзор маршрутов — опционально |

---

## Учебная программа

Последовательность модулей: **D0** (инфраструктура) → **D1/T1** (HTTP, Client) → **D2/T2** (ORM) → **S1** (PostgreSQL, SQL) → **D3–D5B** (DRF, auth, Device Inventory) → **T6** (httpx, Pydantic, Allure) → **D6/T6b** (Compose, GHA).

Полное описание модулей, результатов обучения и артефактов: **[docs/PLAN.md](docs/PLAN.md)** (также EN/PL).

### Статус реализации (ревизия репозитория)

| Модуль | Артефакт |
|--------|----------|
| D0 | `config/`, `manage.py`, `requirements.txt`, документация |
| D1 | `core/`, `GET /health/`, `include` routing |
| D1.2 | `load_dotenv`, `SECRET_KEY` / `DEBUG` / `ALLOWED_HOSTS` из env |
| T1 | `tests/test_health.py` |

---

## Дальнейшее развитие

| Этап | Содержание |
|------|------------|
| Маршрутизация | именованные URL, `reverse`, тест 404 (D1.3) |
| Персистентность | модель `Device`, миграции, admin |
| API | DRF ViewSets, аутентификация, фильтрация |
| Домен | heartbeat, DFU — паритет с `device_lab` |
| Качество | pytest-django, покрытие API, Allure |
| Доставка | Dockerfile, `docker-compose.yml`, workflow CI |

---

## Ссылки

- Репозиторий: https://github.com/ANDRZEJSZAMBORSKI/device_inventory_api  
- Сопутствующий QA / mock API: https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep  
- Django 5.2 documentation: https://docs.djangoproject.com/en/5.2/
