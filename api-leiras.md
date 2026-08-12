## API-leírás

A FastAPI által automatikusan generált, teljes körű OpenAPI (Swagger) dokumentáció a /docs útvonalon érhető el. Ott a végpontok nemcsak megtekinthetők, hanem élőben tesztelhetők is.

Főbb végpontok:

GET /: Navigációs és belépési információs végpont.

GET /api/spots: Lekérdezi az összes elérhető parkolóhelyet és azok típusait.

GET /api/spots/{spot_id}/bookings: Visszaadja egy adott parkolóhelyhez tartozó összes eddigi foglalást.

POST /api/bookings: Új foglalási kérést fogad. A bejövő (payload) adatok között szerepelnie kell a parkolóhely azonosítójának, a kérelmező nevének, valamint a kezdő és záró időpontnak. A végpont integrált ütközésvizsgálattal rendelkezik (HTTP 409 Conflict hibát ad vissza ütközés esetén).

DELETE /api/bookings/{booking_id}: Egy létező foglalás lemondása (státuszváltás cancelled-re).