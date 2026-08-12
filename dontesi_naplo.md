# Döntési Napló és Reflexió

## 1. Döntési pontok

| Döntési pont | Amit választottál | Miért | Milyen alternatívát vetettél el |
| :--- | :--- | :--- | :--- |
| **Projekt könyvtárszerkezete** | Moduláris (mappás) struktúra (api, db, schemas, tests) | Jobb átláthatóság, a felelősségi körök tiszta szétválasztása és a jövőbeli skálázhatóság miatt. Bár a javasolt időkeret rövid volt, a karbantarthatóság érdekében ez a profibb megközelítés. | Lapos (flat) struktúra (minden egyetlen mappában). |
| **Időpont-ütközések vizsgálata** | SQL szintű szűrés (`start < end` ÉS `end > start` logikával) | Nagyobb terhelés és adatmennyiség esetén is gyors marad. A relációs motorok erre vannak optimalizálva. | A foglalások memóriába töltése és Python szintű iterálása (később teljesítményproblémát okozna). |
| **Foglalás lemondása** | "Soft delete" státuszváltással (Enum) | Auditálhatósági szempontból hasznos látni a lemondott foglalásokat, egy termelésben lévő rendszernél az adatok fizikai törlése ritkán jó gyakorlat. | A rekord fizikai törlése a `bookings` táblából (`DELETE` SQL parancs). |
| **Teszt adatbázis** | In-memory SQLite (`sqlite:///:memory:`) a tesztek futtatásához | A tesztek így villámgyorsan lefutnak, és nem szemetelik tele a fő PostgreSQL adatbázist a Docker konténerben. Teljesen izolált tesztkörnyezetet biztosít. | A Dockerben futó fizikai PostgreSQL adatbázis használata a tesztekhez. |
| **Titkos adatok (jelszavak) és környezeti változók kezelése** | A jelszavak (pl. `adminpassword`) közvetlen (hardcoded) megadása a `docker-compose.yml` fájlban, és a verziókövetőbe való feltöltése. | A feladat kifejezett elvárása, hogy a teljes rendszer egyetlen paranccsal (pl. `docker-compose up`) induljon, és azonnal tesztelhető legyen[cite: 1]. Ha elrejtett `.env` fájlt használtam volna, az értékelőnek manuálisan kellene beállítania a környezeti változókat futtatás előtt. | A biztonságos, iparági standard megoldás: a hitelesítési adatok szigorú kihagyása a repóból (`.gitignore`), és lokális `.env` fájlból vagy egy dedikált Secrets Managerből való beolvasás (éles termelési környezetben ez lenne a kötelező). |



