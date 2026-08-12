## Felhasználói Kézikönyv (Futtatás és Tesztelés)

A rendszer teljes egészében konténerizált, így a futtatásához kizárólag a **Docker** és a **Docker Compose** megléte szükséges.

### 1. A rendszer elindítása
A teljes alkalmazás (a backend szolgáltatás és az adatbázis) egyetlen paranccsal elindítható, előre inicializált állapotban. A terminálban, a projekt gyökerében futtasd a következőt:

```bash
docker compose up --build 
```
Megjegyzés: A rendszer induláskor automatikusan létrehozza az adatbázis sémát, és feltölti 5 darab alapértelmezett parkolóhellyel (standard, mozgáskorlátozott és elektromos töltő típusokkal), így azonnal tesztelhető.

### 2. Hozzáférés a felülethez
Sikeres indulás után az API interaktív dokumentációja (Swagger UI) azonnal elérhető a böngészőből:
👉 [Swagger UI dokumentáció](http://localhost:8000/docs)   

### 3. Tesztek futtatása
A projekt tartalmazza a kritikus üzleti logikát ellenőrző integrációs teszteket. A tesztek futtatásához hagyd futni a rendszert a háttérben, és egy új terminálablakban add ki ezt a parancsot:

```bash
docker compose exec backend pytest tests/ -v
```
