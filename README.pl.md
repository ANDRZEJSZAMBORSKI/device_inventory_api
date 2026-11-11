# Device Inventory API

**PL** · [RU](README.md) · [EN](README.en.md)

<!-- readme-preamble -->

**Device Inventory API** to repozytorium **Django** obejmujące pełny cykl: warstwa HTTP, baza danych (SQLite → PostgreSQL), **DRF**, domena inwentaryzacji urządzeń, testy automatyczne, kontenery i CI. Kontynuacja [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep): mock `device_lab` realizowany jako **backend** (stany urządzeń, heartbeat, DFU).

Dokument: **instrukcja eksploatacji** oraz **podręcznik** architektury Django powiązany z kodem. Języki: [RU](README.md), [EN](README.en.md), **PL** (ten plik). Program kursu: [docs/PLAN.pl.md](docs/PLAN.pl.md).

### Cel systemu

Warstwy: Django MTV, PostgreSQL, DRF, zestaw testów (`Client`, APITestCase, pytest-django, httpx), Docker Compose i GitHub Actions.

### Powiązanie z hp-qa-junior-prep

Mock in-memory i MockTransport → ORM + Postgres; testy `device_lab` → testy API tego serwisu.

### Szybki start

```bash
cd /d/pyton_2/git/device_inventory_api
source .venv/Scripts/activate
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py runserver
python manage.py test tests.test_health -v 2
```

### Struktura

`config/` — ustawienia projektu. `core/` — widoki i trasy aplikacji. `tests/` — testy projektu. `docs/` — program nauczania.

### Moduł D1 — HTTP i MTV

**MTV:** Model (dane), Template (prezentacja), View (obsługa żądań). Obecna wersja: View `health` w `core/views.py`.

**HttpRequest** — metoda, ścieżka, `GET`/`POST`, nagłówki, użytkownik, sesja. Endpoint `/health/` zwraca JSON diagnostyczny (także do testów regresji).

**JsonResponse** dla prostego JSON; **DRF** w modułach CRUD.

### Kontrakt GET /health/

Ścieżka `/health/`, status 200, nagłówek `X-API-Version: 1.0`, pole `status: ok` oraz odwzorowanie pól żądania. Powtarzalne parametry query jako listy w `GET`.

### Routing

`config/urls.py` → `include("core.urls")`; `core/urls.py` → `health/`.

### django.test.Client

Pełny stos Django in-process, bez serwera TCP. **httpx** — testy przez prawdziwy HTTP (późniejszy moduł).

Plik `tests/test_health.py`: GET, query, QueryDict.

### Program nauczania

Szczegóły: **[docs/PLAN.pl.md](docs/PLAN.pl.md)**. Zrealizowano: D0, D1 `/health/`, T1.

### Odnośniki

https://github.com/ANDRZEJSZAMBORSKI/device_inventory_api · https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep
