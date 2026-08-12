from fastapi import FastAPI

app = FastAPI(title="Parkolóhely-foglalás API")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "A rendszer fut!"}