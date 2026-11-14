# Device Inventory API

**PL** · [RU](README.md) · [EN](README.en.md)

<!-- readme-preamble -->

**Device Inventory API** to repozytorium **Django** obejmujące pełny cykl: warstwa HTTP, baza danych (SQLite → PostgreSQL), **DRF**, domena inwentaryzacji urządzeń, testy automatyczne, kontenery i CI. Kontynuacja [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep): mock `device_lab` realizowany jako **backend** (stany urządzeń, heartbeat, DFU).

Dokument: **instrukcja eksploatacji** oraz **podręcznik** architektury Django powiązany z kodem. Języki: [RU](README.md), [EN](README.en.md), **PL** (ten plik). Program kursu: [docs/PLAN.pl.md](docs/PLAN.pl.md).

### Cel systemu

| Warstwa | Odpowiedzialność |
|---------|------------------|
| **Django (MTV)** | routing HTTP, widoki, ORM, admin |
| **PostgreSQL** | docelowy silnik po module S1 |
| **DRF** | REST, serializacja, uwierzytelnianie |
| **Testy** | `Client`, `APITestCase`, pytest-django, httpx |
| **Dostawa** | Docker Compose, GitHub Actions |

### Powiązanie z hp-qa-junior-prep

| hp-qa | To repozytorium |
|-------|-----------------|
| Pydantic `Device`, `InMemoryInventory` | model Django `inventory.Device` |
| `device_lab` testy mock HTTP | `tests/test_device_model.py`, później API |
| MockTransport | ORM + transakcje Postgres |

### Wymagania

Python ≥ 3.11, Django 5.2.x, Git. PostgreSQL opcjonalnie (`DB_ENGINE=postgresql`). Docker — moduł D6.

### Mapa dokumentacji

| Rozdział | Temat | Kod |
|----------|-------|-----|
| [Szybki start](#szybki-start) | venv, migrate, testy | katalog główny |
| [Struktura](#struktura-repozytorium) | `inventory`, `tests` | — |
| [D2 — model Device](#moduł-d2--orm-i-model-device) | ORM, migracje | `inventory/models.py` |
| [T2 — testy ORM](#moduł-t21--testowanie-orm) | TestCase, transakcje | `tests/test_device_model.py` |
| [Baza danych](#konfiguracja-bazy-db_engine) | `DB_ENGINE` | `.env.example` |

### Spis treści

1. [Szybki start](#szybki-start)
2. [Struktura repozytorium](#struktura-repozytorium)
3. [Moduł D1 — HTTP i MTV](#moduł-d1--http-i-mtv)
4. [Kontrakt GET /health/](#kontrakt-get-health)
5. [Routing](#routing)
6. [django.test.Client](#djangotestclient)
7. [Moduł D1.2 — konfiguracja](#moduł-d12--konfiguracja-12-factor)
8. [Moduł D1.3 — nazwane trasy](#moduł-d13--nazwane-trasy)
9. [Kontrakt GET /version/](#kontrakt-get-version)
10. [Konfiguracja bazy](#konfiguracja-bazy-db_engine)
11. [Moduł D2 — ORM i model Device](#moduł-d2--orm-i-model-device)
12. [Moduł T2.1 — testowanie ORM](#moduł-t21--testowanie-orm)
13. [Polecenia testów](#polecenia-testów)
14. [Status programu](#status-programu-nauczania)
15. [Kolejne kroki](#kolejne-kroki)

---

## Szybki start

```bash
cd /d/pyton_2/git/device_inventory_api
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env   # DJANGO_SECRET_KEY, DB_ENGINE
python manage.py check
python manage.py migrate
python manage.py runserver
```

Regresja (HTTP + routing + ORM na SQLite):

```bash
python manage.py test tests.test_device_model tests.test_routing tests.test_health -v 2
```

Shell — utworzenie urządzenia:

```bash
python manage.py shell -c "from inventory.models import Device; d=Device.objects.create(); print(d.device_id, d.state)"
```

Bez `DJANGO_SECRET_KEY` lub poprawnego `DB_ENGINE` start się nie powiedzie (`ValueError`).

---

## Struktura repozytorium

```text
config/       — ustawienia projektu
core/         — HTTP: health, version
inventory/    — domena: Device, migracje (D2)
tests/        — test_health, test_routing, test_device_model
docs/         — PLAN (RU/EN/PL)
```

W `config/urls.py` zarezerwowano prefiks **`inventory/`** (`include("inventory.urls")`); endpointy REST — w D3–D5.

---

## Moduł D1 — HTTP i MTV

**MTV:** Model (dane), Template, View. Obecnie widoki w `core`; model domenowy — **`inventory.Device`**.

**HttpRequest** — metoda, ścieżka, query, nagłówki, użytkownik. `/health/` — JSON diagnostyczny.

**JsonResponse** na etapie D1; **DRF** w modułach CRUD.

### Kontrakt GET /health/

Ścieżka `/health/`, status 200, nagłówek `X-API-Version: 1.0`, pole `status: ok`, odbicie pól żądania.

### Routing

`core/urls.py`: `health/`, `version/` z `name=`. Testy: `tests/test_routing.py`.

### django.test.Client

Pełny stos Django in-process. **httpx** — później przeciw prawdziwemu HTTP.

### Moduł D1.2 — konfiguracja (12-factor)

`load_dotenv` w `config/settings.py`. Zmienne: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`. Szablon: `.env.example`.

### Moduł D1.3 — nazwane trasy

`reverse`, `resolve`, różnica `NoReverseMatch` / HTTP 404. `GET /version/` — metadane API.

---

## Kontrakt GET /version/

JSON: `api`, `module` — stub przed OpenAPI (D5).

---

## Konfiguracja bazy (`DB_ENGINE`)

| Wartość | Silnik | Zastosowanie |
|---------|--------|--------------|
| `sqlite` | SQLite | dev, szybkie testy ORM |
| `postgresql` | PostgreSQL | S1, blokady, izolacja transakcji |

Zmienne Postgres: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (patrz `.env.example`).

SQLite: `transaction_mode: IMMEDIATE`, osobna baza testowa `TEST.NAME`. Zależność **`psycopg`** w `requirements.txt`.

```bash
python manage.py migrate
python manage.py dbshell
```

---

## Moduł D2 — ORM i model Device

### Cel

Persystencja domeny **inwentarz urządzeń**: migracje, ORM, zgodność wartości `state` z mockiem **`device_lab`**.

### Pydantic vs Django

| | mock `device_lab` | `inventory.Device` |
|---|-------------------|---------------------|
| Rola | walidacja dict | wiersz w bazie + ORM |
| ID | podawane przy rejestracji | **autogeneracja** `device-NNN` w `save()` |
| Stany | StrEnum | `DeviceStatus` (TextChoices) |

### Pola modelu

| Pole | Znaczenie |
|------|-----------|
| `device_id` | PK, np. `device-001` |
| `firmware_version` | domyślnie `1.0.0` |
| `state` | `online` / `offline` / `dfu_in_progress` |
| `last_seen_at` | nullable, do heartbeat w D5 |
| `created_at`, `updated_at` | audyt |

**`Meta.ordering`** — sortowanie po części numerycznej id.

**`DeviceQuerySet.ordered_by_device_number()`** — materiał dydaktyczny (jawne sortowanie querysetu).

### Generacja `device_id`

W **`transaction.atomic()`**:

- **SQLite:** maks. numer + 1;
- **PostgreSQL:** `DeviceCounter` + `select_for_update`.

Migracje: `0001`, `0002` (seed licznika), `0003` (opcje modelu).

---

## Moduł T2.1 — testowanie ORM

Plik: **`tests/test_device_model.py`** (~58 testów modelu + laboratorium transakcji).

| Klasa bazowa | Zastosowanie |
|--------------|--------------|
| **TestCase** | szybkie testy ORM, `setUpTestData`, `IntegrityError` |
| **TransactionTestCase** | wątki, `select_for_update`, savepointy |

`manage.py test` używa **osobnej bazy testowej** — nie niszczy dev `db.sqlite3`.

Część testów (izolacja, `SKIP LOCKED`, retry serializacji) — **`skipTest` na SQLite**, pełny przebieg na Postgres (S1).

Oczekiwany wynik na SQLite w pakiecie z T1:

```bash
python manage.py test tests.test_device_model tests.test_routing tests.test_health -v 2
```

→ OK, ~15 pominiętych (PostgreSQL).

---

## Polecenia testów

| Polecenie | Cel |
|-----------|-----|
| `python manage.py test tests.test_device_model tests.test_routing tests.test_health -v 2` | główna regresja |
| `python manage.py test tests.test_device_model -v 2` | sam D2/T2 |

---

## Status programu nauczania

Szczegóły: **[docs/PLAN.pl.md](docs/PLAN.pl.md)**.

| Moduł | Artefakt |
|-------|----------|
| D0–D1.3, T1 | `core`, health, routing, config |
| **D2** | `inventory`, `Device`, migracje, `DB_ENGINE` |
| **T2.1** | `test_device_model.py` |

**Kolejny:** S1 (Postgres + `docs/SQL.md`) lub D3 (DRF).

---

## Kolejne kroki

| Etap | Treść |
|------|--------|
| S1 | Postgres bez skip, SQL ↔ ORM |
| D3–D5B | REST, auth, DFU jak w `device_lab` |
| T6 | httpx, Allure |
| D6/T6b | Compose, GHA |

---

## Odnośniki

https://github.com/ANDRZEJSZAMBORSKI/device_inventory_api · https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep · https://docs.djangoproject.com/en/5.2/