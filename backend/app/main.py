# app/main.py
from fastapi import FastAPI
from app.api.v1 import auth, trips, travel_twin

app = FastAPI(title="VoyageAI API")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(trips.router, prefix="/api/v1")
app.include_router(travel_twin.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}