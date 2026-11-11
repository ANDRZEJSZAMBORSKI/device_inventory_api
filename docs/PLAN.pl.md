# Program nauczania: Device Inventory API

**PL** · [RU](PLAN.md) · [EN](PLAN.en.md)

**Wersja:** 2026-11-11  
**Repozytorium:** https://github.com/ANDRZEJSZAMBORSKI/device_inventory_api  
**Praktykum wstępne:** https://github.com/ANDRZEJSZAMBORSKI/hp-qa-junior-prep (`device_lab`)

---

## 1. Cele programu

Pełny cykl usługi webowej Django: HTTP, schemat danych, PostgreSQL, DRF, testy warstwowe, Docker Compose, GitHub Actions. Domena: **inwentaryzacja urządzeń** (online/offline, heartbeat, DFU), zgodna ze specyfikacją mock `device_lab`.

---

## 2. Efekty uczenia się

MTV i cykl żądania; urlconf modułowy; views i JSON; ORM i SQL; Client i APITestCase; REST i auth; scenariusze DFU; httpx/Allure; Compose i CI.

---

## 3. Struktura

| Blok | Moduły |
|------|--------|
| I | D0, D1, T1 — infrastruktura, HTTP, Client |
| II | D2, T2, S1 — ORM, Postgres |
| III | D3–D5B, T3–T5 — DRF, domena |
| IV | T6 — httpx, Pydantic, Allure |
| V | D6, T6b — kontenery, GHA |

Szacowany nakład: 200–280 godzin pracy z kodem i dokumentacją.

---

## 4. Blok I — zrealizowane elementy

- **D0:** projekt `config`, zależności, dokumentacja trójjęzyczna.
- **D1:** `core`, endpoint `/health/`, `JsonResponse`, routing `include`.
- **T1:** `tests/test_health.py`, `QueryDict`, Client.

**Kolejny moduł:** D1.2 konfiguracja (`dotenv`, secrets).

---

## 5. Blok II–V

D2 model Device; S1 `docs/SQL.md`; D3–D5B REST i DFU; T6 httpx; D6 Compose; T6b Actions.

---

## 6. Artefakty

README/PLAN (RU/EN/PL), `docs/API.md`, `docs/SQL.md`, `docker-compose.yml`, workflow CI, Allure.

---

## 7. Metodyka

Wersjonowanie w Git; aktualizacja dokumentacji po każdym bloku; regresja testami.

---

## 8. Literatura

Dokumentacja Django 5.2, DRF, PostgreSQL.
