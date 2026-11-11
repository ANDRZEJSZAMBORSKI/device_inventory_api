# Plan nauki: Device Inventory API

**PL** · [RU](PLAN.md) · [EN](PLAN.en.md)

**Aktualizacja:** 2026-11-11  
**Repo:** `device_inventory_api`  
**Kontynuacja:** [`hp-qa-junior-prep`](https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep) — mock `device_lab` → **prawdziwy** backend Django.

---

## 1. Cel projektu

Jeden **portfolio backend** z **pełnym programem**:

| Warstwa | Zakres |
|---------|--------|
| **Django** | MTV, settings, URL, szablony wg potrzeb |
| **Baza** | SQLite → **PostgreSQL**, ORM, migracje, SQL |
| **API** | DRF: serializery, ViewSet, auth, walidacja |
| **Domena** | Inventory urządzeń, heartbeat, DFU — jak `device_lab` |
| **Testy** | TestCase, APITestCase, **pytest-django**, asercje DB |
| **QA automation** | **httpx** + **Pydantic** + **Allure** |
| **Infra** | **Docker**, **Compose**, **GitHub Actions** |

**Tryb:** TZ → kod po Twojej stronie → teoria → review. Bez zmian logiki bez zgody.

---

## 2. Postęp

| Moduł | Status |
|-------|--------|
| **D0** | prawie: brak **git** + commit dokumentacji |
| **D1.1 + T1.1** | **następny** krok |
| Blok A | otwarty |
| B–D | zablokowane do zaliczenia A |

Django w CV dopiero po **bloku A**.

---

## 3. Kolejność (obowiązkowa)

```text
Blok A — Django core: D0 → D1/T1 → D2/T2 → S1
Blok B — API: D3/T3 → D4/T4 → D5/T5 → D5B
Blok C — T6 (httpx, Allure)
Blok D — D6 Compose + T6b GHA
```

Moduły **D** i **T** zdawane razem.

---

## 4. Skrót modułów

- **D0:** venv, Django 5, check, migrate, README/PLAN PL/EN/RU, git.
- **D1/T1:** health, Client, dotenv (D1.2).
- **D2/T2:** model Device, pytest-django.
- **S1:** Postgres, `docs/SQL.md`.
- **D3–D5B:** DRF, auth, CRUD, DFU/heartbeat jak w mocku hp-qa.
- **T6:** httpx + Allure przeciw działającemu serwisowi.
- **D6/T6b:** kontenery web+db, workflow CI, artefakt Allure.

---

## 5. Struktura docelowa

`apps/`, `tests/`, `docs/`, `docker-compose.yml`, `.github/workflows/`.

---

## 6. DoD całego tracku

ORM, warstwy testów, HTTP+Postgres, DRF, Compose, zielony CI.

---

## 7. Zaliczenie modułu

Git, output komend, teoria, review.

---

## 8. Czas (~8–12 h/tydz.)

A: 2–3 tyg. · B: 4–6 · C–D: 2–3.

---

## 9. Poza zakresem (na razie)

Celery, Kafka, K8s, GraphQL.

---

## 10. Następny krok

Domknąć **D0** (git + docs) → **D1.1 + T1.1**.
