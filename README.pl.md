# Device Inventory API

**PL** · [RU](README.md) · [EN](README.en.md)

<!-- readme-preamble -->

**Device Inventory API** to projekt portfolio na **Django**: backend, baza danych, REST API, testowanie w ekosystemie Django, potem **Docker / Docker Compose** i **GitHub Actions**. To **kontynuacja** repozytorium szkoleniowego [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep): tam mock **Device Inventory** (`device_lab`, HTTP mocki, pytest, Allure, CI); **tu** — **prawdziwy** serwis Django/DRF + **PostgreSQL**, ten sam domen (urządzenia, heartbeat, DFU, stany online/offline).

| Etap | Status 2026-11-11 |
|------|-------------------|
| **D0** — bootstrap (venv, `startproject`, git) | w toku |
| **D1–D6, T1–T6, S1, T6b** | [docs/PLAN.pl.md](docs/PLAN.pl.md) |

Pełny program: Django **bez** DRF → modele/ORM → Postgres/SQL → DRF → auth → Inventory API → pytest-django / APITestCase → **httpx** + Pydantic + Allure → **kontenery + GHA**.

### Dla kogo

- Junior **Python / Backend / QA**, który przeszedł automatyzację API w `hp-qa-junior-prep` i buduje **pełny backend** do CV.
- Kto chce pokazać historię **mock → API produkcyjnego stylu** w jednej domenie.

### Powiązanie z hp-qa-junior-prep

| hp-qa-junior-prep | device_inventory_api |
|-------------------|----------------------|
| `src/device_lab/` — in-memory + `MockTransport` | modele Django + Postgres |
| `tests/device_lab/` (~76 testów) | `tests/` — TestCase, APITestCase, pytest-django, później httpx |
| Compose + MockServer + GHA | Compose **web + db + test job** + GHA w tym repo |
| Pydantic `Device`, maszyna stanów | serializery DRF + te same przejścia (D5B) |

### Wymagania

| Składnik | Uwaga |
|----------|--------|
| Python | **≥ 3.11** |
| Git | od D0 |
| Docker Desktop | blok **D6** |
| PostgreSQL | blok **S1** |

### Dokumentacja

| Plik | Język |
|------|--------|
| [docs/PLAN.md](docs/PLAN.md) | RU |
| [docs/PLAN.en.md](docs/PLAN.en.md) | EN |
| [docs/PLAN.pl.md](docs/PLAN.pl.md) | PL — pełny plan modułów |

### Szybki start (D0)

```bash
cd /d/pyton_2/git/device_inventory_api
source .venv/Scripts/activate

python manage.py check
python manage.py migrate
python manage.py runserver
```

`http://127.0.0.1:8000/` — strona powitalna Django. Sekrety: `.env.example` → `.env` (podłączenie w **D1.2**).

### Struktura docelowa

Rosnie moduł po module: `apps/devices/`, `tests/`, `docker-compose.yml`, `.github/workflows/`.

### Cel końcowy

REST + auth + heartbeat/DFU, Postgres, pełne testy, Compose, GitHub Actions.

### Tryb nauki

TZ → kod i testy po Twojej stronie → teoria → review. Logiki projektu **nie zmieniamy** bez Twojej zgody (jak w `hp-qa-junior-prep`).
