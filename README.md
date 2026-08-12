# Parkolóhely-foglalás API

Ez a projekt egy backend szolgáltatás, amely egy parkoló foglalási rendszerét valósítja meg. A rendszer képes nyilvántartani a különböző típusú parkolóhelyeket, fogadni és validálni a foglalási kéréseket, valamint kezelni a foglalások lemondását.

---

## 1. Felhasználói Kézikönyv (Futtatás és Tesztelés)

A rendszer teljes egészében konténerizált, így a futtatásához kizárólag a **Docker** és a **Docker Compose** megléte szükséges.

### 1.1. A rendszer elindítása
A teljes alkalmazás (a backend szolgáltatás és az adatbázis) egyetlen paranccsal elindítható, előre inicializált állapotban. A terminálban, a projekt gyökerében futtasd a következőt:

```bash
docker compose up --build 
```
Megjegyzés: A rendszer induláskor automatikusan létrehozza az adatbázis sémát, és feltölti 5 darab alapértelmezett parkolóhellyel (standard, mozgáskorlátozott és elektromos töltő típusokkal), így azonnal tesztelhető.

### 1.2. Hozzáférés a felülethez
Sikeres indulás után az API interaktív dokumentációja (Swagger UI) azonnal elérhető a böngészőből:
👉 [Swagger UI dokumentáció](http://localhost:8000/docs)   

### 1.3. Tesztek futtatása
A projekt tartalmazza a kritikus üzleti logikát ellenőrző integrációs teszteket. A tesztek futtatásához hagyd futni a rendszert a háttérben, és egy új terminálablakban add ki ezt a parancsot:

```bash
docker compose exec backend pytest tests/ -v
```

---

## 2. Rendszerterv

### 2.1. Architektúra és Technológiai Stack
A megoldás egy moduláris felépítésű REST API, amely a következő technológiákra épül:

Backend: Python 3.11 + FastAPI. A FastAPI modern, aszinkron támogatással rendelkező keretrendszer, amely beépített Pydantic validációt és automatikus OpenAPI dokumentációt biztosít.

Adatbázis: PostgreSQL 15. Relációs adatbázis-kezelő, amely tranzakcionális biztonságot (ACID) nyújt.

ORM: SQLAlchemy az adatbázis-kapcsolat és a modellek kezelésére.

Infrastruktúra: Docker és Docker Compose a szeparált, környezetfüggetlen futtatásért.

### 2.2. Teljesítmény és Skálázhatósági Megfontolások
A rendszer egyik legkritikusabb pontja a foglalások időpont-ütközésének (overlap) vizsgálata.

Adatbázis szintű validáció: Az ütközésvizsgálatot nem az alkalmazás memóriájában (pl. Python listákon iterálva) végezzük, hanem az SQL motorra bízzuk. A relációs szűrés (start_time < uj_end ÉS end_time > uj_start) biztosítja, hogy a rendszer nagy terhelés és több tízezer rekord esetén is ezredmásodpercek alatt döntsön a kérés elfogadhatóságáról.

Indexelés: Az adatbázis sémában az azonosítók (ID-k) és a parkolóhelyek nevei indexelve vannak a gyorsabb keresés érdekében.

Soft Delete: A lemondott foglalásokat a rendszer nem törli fizikailag (így elkerülhető az adatbázis töredezettsége, és megmarad az audit-nyomvonal), hanem állapotváltozással (cancelled státusz) kezeli.

### 2.3. Projekt Könyvtárszerkezet
A kód backend mappán belüli szerkezete a "Clean Architecture" alapelveit követi:

/api: A HTTP végpontok (routok) és a kéréskezelés helye.

/db: Az adatbázis-kapcsolat és az SQLAlchemy modellek (táblák) definíciója.

/schemas: A Pydantic adatcsere- és validációs modellek.

/tests: Az izolált (in-memory SQLite) adatbázist használó integrációs tesztek.

---

## 3. API-leírás

A FastAPI által automatikusan generált, teljes körű OpenAPI (Swagger) dokumentáció a /docs útvonalon érhető el. Ott a végpontok nemcsak megtekinthetők, hanem élőben tesztelhetők is.

Főbb végpontok:

GET /: Navigációs és belépési információs végpont.

GET /api/spots: Lekérdezi az összes elérhető parkolóhelyet és azok típusait.

GET /api/spots/{spot_id}/bookings: Visszaadja egy adott parkolóhelyhez tartozó összes eddigi foglalást.

POST /api/bookings: Új foglalási kérést fogad. A bejövő (payload) adatok között szerepelnie kell a parkolóhely azonosítójának, a kérelmező nevének, valamint a kezdő és záró időpontnak. A végpont integrált ütközésvizsgálattal rendelkezik (HTTP 409 Conflict hibát ad vissza ütközés esetén).

DELETE /api/bookings/{booking_id}: Egy létező foglalás lemondása (státuszváltás cancelled-re).