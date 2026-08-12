## Rendszerterv

### 1. Architektúra és Technológiai Stack
A megoldás egy moduláris felépítésű REST API, amely a következő technológiákra épül:

Backend: Python 3.11 + FastAPI. A FastAPI modern, aszinkron támogatással rendelkező keretrendszer, amely beépített Pydantic validációt és automatikus OpenAPI dokumentációt biztosít.

Adatbázis: PostgreSQL 15. Relációs adatbázis-kezelő, amely tranzakcionális biztonságot (ACID) nyújt.

ORM: SQLAlchemy az adatbázis-kapcsolat és a modellek kezelésére.

Infrastruktúra: Docker és Docker Compose a szeparált, környezetfüggetlen futtatásért.

### 2. Teljesítmény és Skálázhatósági Megfontolások
A rendszer egyik legkritikusabb pontja a foglalások időpont-ütközésének (overlap) vizsgálata.

Adatbázis szintű validáció: Az ütközésvizsgálatot nem az alkalmazás memóriájában (pl. Python listákon iterálva) végezzük, hanem az SQL motorra bízzuk. A relációs szűrés (start_time < uj_end ÉS end_time > uj_start) biztosítja, hogy a rendszer nagy terhelés és több tízezer rekord esetén is ezredmásodpercek alatt döntsön a kérés elfogadhatóságáról.

Indexelés: Az adatbázis sémában az azonosítók (ID-k) és a parkolóhelyek nevei indexelve vannak a gyorsabb keresés érdekében.

Soft Delete: A lemondott foglalásokat a rendszer nem törli fizikailag (így elkerülhető az adatbázis töredezettsége, és megmarad az audit-nyomvonal), hanem állapotváltozással (cancelled státusz) kezeli.

### 3. Projekt Könyvtárszerkezet
A kód backend mappán belüli szerkezete a "Clean Architecture" alapelveit követi:

/api: A HTTP végpontok (routok) és a kéréskezelés helye.

/db: Az adatbázis-kapcsolat és az SQLAlchemy modellek (táblák) definíciója.

/schemas: A Pydantic adatcsere- és validációs modellek.

/tests: Az izolált (in-memory SQLite) adatbázist használó integrációs tesztek.