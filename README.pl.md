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
cp .env.example .env   # ustaw DJANGO_SECRET_KEY
python manage.py runserver
python manage.py test tests.test_routing tests.test_health -v 2
```

```bash
python manage.py shell -c "from django.urls import reverse; print(reverse('health'), reverse('version'))"
```

Bez `DJANGO_SECRET_KEY` uruchomienie się nie powiedzie (`ValueError`).

### Struktura

`config/` — ustawienia projektu. `core/` — widoki i trasy aplikacji. `tests/` — testy projektu. `docs/` — program nauczania.

### Moduł D1 — HTTP i MTV

**MTV:** Model (dane), Template (prezentacja), View (obsługa żądań). Obecna wersja: View `health` w `core/views.py`.

**HttpRequest** — metoda, ścieżka, `GET`/`POST`, nagłówki, użytkownik, sesja. Endpoint `/health/` zwraca JSON diagnostyczny (także do testów regresji).

**JsonResponse** dla prostego JSON; **DRF** w modułach CRUD.

### Kontrakt GET /health/

Ścieżka `/health/`, status 200, nagłówek `X-API-Version: 1.0`, pole `status: ok` oraz odwzorowanie pól żądania. Powtarzalne parametry query jako listy w `GET`.

### Routing

`config/urls.py` → `include("core.urls")`.

`core/urls.py`: `health/` (`name="health"`), `version/` (`name="version"`).

**`reverse(name)`** — URL bez wpisywania ścieżki na sztywno. **`resolve(path)`** — dopasowanie widoku i nazwy trasy. **`path()`** zamiast starego `url(regex)`.

### Moduł D1.3

Testy: `tests/test_routing.py` (reverse, resolve, HTTP 404, `NoReverseMatch`).

`GET /version/` → JSON: `api`, `module` (metadane przed OpenAPI).

### django.test.Client

Pełny stos Django in-process, bez serwera TCP. **httpx** — testy przez prawdziwy HTTP (późniejszy moduł).

Plik `tests/test_health.py`: GET, query, QueryDict.

### Moduł D1.2 — konfiguracja (12-factor)

Konfiguracja **poza kodem**: `.env` lokalnie (poza gitem), `.env.example` jako szablon.

`load_dotenv(BASE_DIR / ".env")` w **`config/settings.py`** — jawna ścieżka do pliku w katalogu projektu; WSGI/ASGI widzi te same zmienne co `manage.py`. Brak `.env` nie kończy `load_dotenv`, ale **`DJANGO_SECRET_KEY` jest wymagany**.

| Zmienna | Rola |
|---------|------|
| `DJANGO_SECRET_KEY` | wymagany |
| `DJANGO_DEBUG` | `1` / `TRUE` → tryb debug |
| `DJANGO_ALLOWED_HOSTS` | dozwolone hosty (bez portu i https) |

`DEBUG=True` — tylko development. `ALLOWED_HOSTS` — ochrona nagłówka Host (także za nginx).

### Program nauczania

Szczegóły: **[docs/PLAN.pl.md](docs/PLAN.pl.md)**. Zrealizowano: D0, D1, D1.2, D1.3, T1 (`test_health`, `test_routing`).

### Odnośniki

https://github.com/ANDRZEJSZAMBORSKI/device_inventory_api · https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep
