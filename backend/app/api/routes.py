from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.revenue import ForecastRequest, PriceRecommendationRequest
from app.services import revenue_intelligence as intelligence

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/forecast")
def forecast(request: ForecastRequest):
    return intelligence.forecast(request)


@router.post("/recommend-price")
def recommend_price(request: PriceRecommendationRequest):
    return intelligence.recommend_price(request)


@router.get("/dashboard")
def dashboard(hotel_id: str = "HRI-BLR-001", room_type: Optional[str] = None, horizon_days: int = Query(default=30, ge=7, le=90)):
    return intelligence.dashboard(hotel_id=hotel_id, room_type=room_type, horizon_days=horizon_days)


@router.get("/booking-pace")
def booking_pace(days: int = Query(default=30, ge=1, le=90), hotel_id: str = "HRI-BLR-001", room_type: Optional[str] = None):
    return intelligence.booking_pace(days, hotel_id=hotel_id, room_type=room_type)


@router.get("/market-demand")
def market_demand(days: int = Query(default=30, ge=1, le=90), hotel_id: str = "HRI-BLR-001"):
    return intelligence.market_demand(days, hotel_id=hotel_id)


@router.get("/competitor-analysis")
def competitor_analysis(room_type: str = "Deluxe", hotel_id: str = "HRI-BLR-001"):
    return intelligence.competitor_analysis(room_type, hotel_id=hotel_id)
