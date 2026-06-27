from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


RoomType = Literal["Deluxe", "Executive", "Suite", "Premium", "Family"]


class ForecastRequest(BaseModel):
    hotel_id: str = "HRI-BLR-001"
    room_type: Optional[RoomType] = None
    horizon_days: int = Field(default=30, ge=1, le=90)


class PriceRecommendationRequest(BaseModel):
    hotel_id: str = "HRI-BLR-001"
    room_type: RoomType = "Deluxe"
    stay_date: Optional[date] = None


class ForecastPoint(BaseModel):
    stay_date: date
    hotel_id: str
    property_name: str
    city: str
    room_type: RoomType
    expected_occupancy: float
    expected_rooms_sold: int
    expected_revenue: float
    adr: float
    revpar: float
    market_demand_index: float


class PricingExplanation(BaseModel):
    factor: str
    impact: float
    detail: str


class PriceRecommendation(BaseModel):
    stay_date: date
    hotel_id: str
    property_name: str
    city: str
    room_type: RoomType
    current_price: float
    recommended_price: float
    suggested_change: float
    expected_occupancy: float
    expected_revenue: float
    confidence_score: float
    explanations: list[PricingExplanation]


class BookingPacePoint(BaseModel):
    stay_date: date
    hotel_id: str
    property_name: str
    city: str
    room_type: RoomType
    actual_bookings: int
    expected_bookings: int
    variance: int
    status: Literal["ahead", "on_track", "behind"]


class CompetitorPrice(BaseModel):
    hotel_name: str
    room_type: RoomType
    listed_price: float
    rating: float


class MarketDemandPoint(BaseModel):
    stay_date: date
    city: str
    holiday_score: float
    festival_score: float
    weather_score: float
    event_score: float
    competitor_price_index: float
    market_demand_index: float


class HotelOption(BaseModel):
    hotel_id: str
    property_name: str
    city: str
    star_rating: float
    room_types: list[RoomType]


class ChannelMixPoint(BaseModel):
    channel: str
    bookings: int
    revenue: float
    share: float


class SegmentPerformancePoint(BaseModel):
    segment: str
    bookings: int
    adr: float
    cancellation_rate: float


class DashboardSummary(BaseModel):
    selected_hotel_id: str
    selected_room_type: Optional[RoomType]
    horizon_days: int
    hotels: list[HotelOption]
    revenue_forecast: float
    occupancy_forecast: float
    adr: float
    revpar: float
    revenue_opportunity: float
    high_demand_dates: list[date]
    low_demand_dates: list[date]
    recommendations: list[PriceRecommendation]
    booking_pace: list[BookingPacePoint]
    forecast: list[ForecastPoint]
    channel_mix: list[ChannelMixPoint]
    segment_performance: list[SegmentPerformancePoint]
