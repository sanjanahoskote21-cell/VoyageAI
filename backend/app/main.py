# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, trips, travel_twin, places

app = FastAPI(title="VoyageAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(trips.router, prefix="/api/v1")
app.include_router(travel_twin.router, prefix="/api/v1")
app.include_router(places.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}