from __future__ import annotations

from datetime import date

from app.schemas.revenue import (
    BookingPacePoint,
    ChannelMixPoint,
    CompetitorPrice,
    DashboardSummary,
    ForecastPoint,
    ForecastRequest,
    HotelOption,
    MarketDemandPoint,
    PriceRecommendation,
    PriceRecommendationRequest,
    PricingExplanation,
    SegmentPerformancePoint,
)
from app.services.synthetic_data import (
    CHANNELS,
    COMPETITORS,
    HOTELS,
    SEGMENTS,
    date_range,
    demand_signals,
    forecast_for,
    hotel_options,
    rooms_for,
)


def _valid_hotel_id(hotel_id: str) -> str:
    return hotel_id if hotel_id in HOTELS else next(iter(HOTELS))


def forecast(request: ForecastRequest) -> list[ForecastPoint]:
    hotel_id = _valid_hotel_id(request.hotel_id)
    rooms = rooms_for(hotel_id)
    room_types = [request.room_type] if request.room_type else list(rooms)
    points = [
        ForecastPoint(**forecast_for(stay_date, hotel_id, room_type))
        for stay_date in date_range(request.horizon_days)
        for room_type in room_types
        if room_type in rooms
    ]
    return points


def market_demand(days: int = 30, hotel_id: str = "HRI-BLR-001") -> list[MarketDemandPoint]:
    hotel_id = _valid_hotel_id(hotel_id)
    city = HOTELS[hotel_id]["city"]
    points: list[MarketDemandPoint] = []
    for stay_date in date_range(days):
        signals = demand_signals(stay_date, hotel_id)
        points.append(
            MarketDemandPoint(
                stay_date=stay_date,
                city=city,
                holiday_score=signals.holiday_score,
                festival_score=signals.festival_score,
                weather_score=signals.weather_score,
                event_score=signals.event_score,
                competitor_price_index=signals.competitor_price_index,
                market_demand_index=signals.market_demand_index,
            )
        )
    return points


def booking_pace(days: int = 30, hotel_id: str = "HRI-BLR-001", room_type: str | None = None) -> list[BookingPacePoint]:
    hotel_id = _valid_hotel_id(hotel_id)
    rooms = rooms_for(hotel_id)
    selected_rooms = [room_type] if room_type else list(rooms)
    points: list[BookingPacePoint] = []
    for stay_date in date_range(days):
        for selected_room in selected_rooms:
            if selected_room not in rooms:
                continue
            room = rooms[selected_room]
            base = forecast_for(stay_date, hotel_id, selected_room)
            expected = round(room["total_rooms"] * base["expected_occupancy"] * 0.58)
            variance = round((base["market_demand_index"] - 0.54) * 13)
            actual = max(expected + variance, 0)
            if variance <= -3:
                status = "behind"
            elif variance >= 3:
                status = "ahead"
            else:
                status = "on_track"
            points.append(
                BookingPacePoint(
                    stay_date=stay_date,
                    hotel_id=hotel_id,
                    property_name=base["property_name"],
                    city=base["city"],
                    room_type=selected_room,
                    actual_bookings=actual,
                    expected_bookings=expected,
                    variance=actual - expected,
                    status=status,
                )
            )
    return points


def competitor_analysis(room_type: str = "Deluxe", hotel_id: str = "HRI-BLR-001") -> list[CompetitorPrice]:
    hotel_id = _valid_hotel_id(hotel_id)
    hotel = HOTELS[hotel_id]
    rooms = rooms_for(hotel_id)
    selected_room = room_type if room_type in rooms else "Deluxe"
    base = rooms[selected_room]["base_price"]
    return [
        CompetitorPrice(
            hotel_name=name,
            room_type=selected_room,
            listed_price=round(base * multiplier, 2),
            rating=rating,
        )
        for name, rating, multiplier in COMPETITORS[hotel["city"]]
    ]


def recommend_price(request: PriceRecommendationRequest) -> PriceRecommendation:
    hotel_id = _valid_hotel_id(request.hotel_id)
    stay_date = request.stay_date or date_range(1)[0]
    room_type = request.room_type if request.room_type in rooms_for(hotel_id) else "Deluxe"
    base = forecast_for(stay_date, hotel_id, room_type)
    room = rooms_for(hotel_id)[room_type]
    pace = next(
        point
        for point in booking_pace(90, hotel_id=hotel_id, room_type=room_type)
        if point.stay_date == stay_date and point.room_type == room_type
    )
    competitors = competitor_analysis(room_type, hotel_id)
    competitor_avg = sum(item.listed_price for item in competitors) / len(competitors)
    current_price = round(room["base_price"] * 1.02, 2)

    occupancy_lift = (base["expected_occupancy"] - 0.68) * 0.38
    demand_lift = (base["market_demand_index"] - 0.55) * 0.3
    pace_lift = min(max(pace.variance / 24, -0.08), 0.12)
    competitor_lift = min(max((competitor_avg / current_price) - 1, -0.08), 0.12) * 0.45
    total_lift = min(max(occupancy_lift + demand_lift + pace_lift + competitor_lift, -0.2), 0.32)

    recommended_price = round(current_price * (1 + total_lift), 2)
    expected_revenue = round(recommended_price * base["expected_rooms_sold"], 2)
    confidence = round(0.64 + min(base["market_demand_index"], 0.9) * 0.24 - abs(total_lift) * 0.16, 2)

    explanations = [
        PricingExplanation(
            factor="Occupancy forecast",
            impact=round(occupancy_lift, 3),
            detail=f"Expected occupancy is {base['expected_occupancy']:.0%} for this stay date.",
        ),
        PricingExplanation(
            factor="Booking pace",
            impact=round(pace_lift, 3),
            detail=f"Current bookings are {abs(pace.variance)} rooms {'above' if pace.variance >= 0 else 'below'} expected pace.",
        ),
        PricingExplanation(
            factor="Market demand index",
            impact=round(demand_lift, 3),
            detail=f"Composite demand score is {base['market_demand_index']:.2f}.",
        ),
        PricingExplanation(
            factor="Competitor pricing",
            impact=round(competitor_lift, 3),
            detail=f"Competitor average listed price is INR {competitor_avg:,.0f}.",
        ),
    ]

    return PriceRecommendation(
        stay_date=stay_date,
        hotel_id=hotel_id,
        property_name=base["property_name"],
        city=base["city"],
        room_type=room_type,
        current_price=current_price,
        recommended_price=recommended_price,
        suggested_change=round(recommended_price - current_price, 2),
        expected_occupancy=base["expected_occupancy"],
        expected_revenue=expected_revenue,
        confidence_score=confidence,
        explanations=explanations,
    )


def channel_mix(forecast_points: list[ForecastPoint]) -> list[ChannelMixPoint]:
    total_revenue = sum(point.expected_revenue for point in forecast_points)
    total_bookings = sum(point.expected_rooms_sold for point in forecast_points)
    points: list[ChannelMixPoint] = []
    for channel, config in CHANNELS.items():
        bookings = round(total_bookings * config["share"])
        revenue = round(total_revenue * config["share"] * config["adr_multiplier"], 2)
        points.append(ChannelMixPoint(channel=channel, bookings=bookings, revenue=revenue, share=round(config["share"], 3)))
    return points


def segment_performance(forecast_points: list[ForecastPoint]) -> list[SegmentPerformancePoint]:
    total_revenue = sum(point.expected_revenue for point in forecast_points)
    total_bookings = max(sum(point.expected_rooms_sold for point in forecast_points), 1)
    base_adr = total_revenue / total_bookings
    points: list[SegmentPerformancePoint] = []
    for segment, config in SEGMENTS.items():
        bookings = round(total_bookings * config["share"])
        points.append(
            SegmentPerformancePoint(
                segment=segment,
                bookings=bookings,
                adr=round(base_adr * config["adr_multiplier"], 2),
                cancellation_rate=config["cancel"],
            )
        )
    return points


def dashboard(hotel_id: str = "HRI-BLR-001", room_type: str | None = None, horizon_days: int = 30) -> DashboardSummary:
    hotel_id = _valid_hotel_id(hotel_id)
    selected_room = room_type if room_type in rooms_for(hotel_id) else None
    horizon_days = min(max(horizon_days, 7), 90)
    forecast_points = forecast(ForecastRequest(hotel_id=hotel_id, room_type=selected_room, horizon_days=horizon_days))
    recommendation_rooms = [selected_room] if selected_room else list(rooms_for(hotel_id))
    recommendations = [
        recommend_price(PriceRecommendationRequest(hotel_id=hotel_id, room_type=room, stay_date=stay_date))
        for stay_date in date_range(min(horizon_days, 14))
        for room in recommendation_rooms
    ]
    total_revenue = sum(point.expected_revenue for point in forecast_points)
    total_available_rooms = sum(rooms_for(hotel_id)[point.room_type]["total_rooms"] for point in forecast_points)
    occupied_rooms = sum(point.expected_rooms_sold for point in forecast_points)
    adr = total_revenue / max(occupied_rooms, 1)
    revpar = total_revenue / max(total_available_rooms, 1)
    high_demand = [point.stay_date for point in forecast_points if point.market_demand_index >= 0.72][:8]
    low_demand = [point.stay_date for point in forecast_points if point.market_demand_index <= 0.45][:8]
    opportunity = sum(max(item.suggested_change, 0) * max(item.expected_occupancy * 10, 4) for item in recommendations)

    return DashboardSummary(
        selected_hotel_id=hotel_id,
        selected_room_type=selected_room,
        horizon_days=horizon_days,
        hotels=[HotelOption(**option) for option in hotel_options()],
        revenue_forecast=round(total_revenue, 2),
        occupancy_forecast=round(occupied_rooms / max(total_available_rooms, 1), 3),
        adr=round(adr, 2),
        revpar=round(revpar, 2),
        revenue_opportunity=round(opportunity, 2),
        high_demand_dates=high_demand,
        low_demand_dates=low_demand,
        recommendations=recommendations,
        booking_pace=booking_pace(min(horizon_days, 30), hotel_id=hotel_id, room_type=selected_room),
        forecast=forecast_points,
        channel_mix=channel_mix(forecast_points),
        segment_performance=segment_performance(forecast_points),
    )
