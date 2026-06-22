from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from datetime import datetime

from services.predictor import PricePredictor
from services.knn_service import KNNService
from services.db_service import DBService
from services.stats_service import StatsService

app = FastAPI(title="MelbProp API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
predictor = PricePredictor()
knn_service = KNNService()
db_service = DBService()
stats_service = StatsService()


class PropertyInput(BaseModel):
    suburb: str
    rooms: int
    type: str  # h, u, t
    method: str
    distance: float
    landsize: float
    building_area: float
    year_built: int
    council_area: Optional[str] = None
    latitude: float
    longitude: float
    bathroom: Optional[int] = 1
    car: Optional[int] = 1


class SuburbCompareInput(BaseModel):
    suburb1: str
    suburb2: str


@app.get("/")
def root():
    return {"message": "MelbProp API is running", "version": "1.0.0"}


@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/predict-price")
async def predict_price(prop: PropertyInput):
    try:
        result = predictor.predict(prop.dict())
        similar = knn_service.find_similar(prop.dict(), n=5)

        # Save to DB
        await db_service.save_prediction({
            "suburb": prop.suburb,
            "rooms": prop.rooms,
            "type": prop.type,
            "distance": prop.distance,
            "landsize": prop.landsize,
            "building_area": prop.building_area,
            "predicted_price": result["predicted_price"],
            "latitude": prop.latitude,
            "longitude": prop.longitude,
        })

        return {
            **result,
            "similar_properties": similar,
            "suburb": prop.suburb,
            "latitude": prop.latitude,
            "longitude": prop.longitude,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/suburb-stats/{suburb}")
async def suburb_stats(suburb: str):
    stats = stats_service.get_suburb_stats(suburb)
    if not stats:
        raise HTTPException(status_code=404, detail="Suburb not found")
    return stats


@app.post("/api/compare-suburbs")
async def compare_suburbs(data: SuburbCompareInput):
    s1 = stats_service.get_suburb_stats(data.suburb1)
    s2 = stats_service.get_suburb_stats(data.suburb2)
    return {"suburb1": s1, "suburb2": s2}


@app.get("/api/suburbs")
def list_suburbs():
    return {"suburbs": stats_service.get_all_suburbs()}


@app.get("/api/history")
async def get_history(limit: int = 20):
    history = await db_service.get_history(limit)
    return {"history": history}


@app.get("/api/price-trends")
def price_trends():
    return stats_service.get_price_trends()


@app.get("/api/model-accuracy")
def model_accuracy():
    return predictor.get_model_stats()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
