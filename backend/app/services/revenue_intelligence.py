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
    """
    Realistic booking pace using an S-curve pickup model.

    The booking curve in hospitality is not linear — most rooms book within
    21 days of the stay date. Expected bookings at any point in time follow
    an S-curve: slow pickup far out, accelerating in the 30-day window,
    heavy in the last 7 days.

    We simulate 'actual' bookings as where we are on that curve today, then
    compare against where we *should* be for a date with this demand profile.
    Weekends and high-demand dates should be tracking ahead; quiet mid-week
    dates should be tracking behind or on track.
    """
    import math

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
            signals = demand_signals(stay_date, hotel_id)
            days_until = max((stay_date - date.today()).days, 0)

            # S-curve pickup: what fraction of final bookings are typically
            # on the books N days before arrival.
            # At 60+ days: ~15%, at 30 days: ~40%, at 14 days: ~65%,
            # at 7 days: ~82%, at 1 day: ~95%
            pickup_fraction = 1.0 / (1.0 + math.exp(0.15 * (days_until - 18)))
            pickup_fraction = round(min(max(pickup_fraction, 0.05), 0.97), 3)

            # Expected bookings = final forecast × pickup fraction
            final_rooms = base["expected_rooms_sold"]
            expected = round(final_rooms * pickup_fraction)

            # Actual bookings vary by demand signals and day-of-week.
            # High-demand dates (events, weekends) book faster than the curve —
            # they track ahead. Quiet mid-week dates book slower — they lag.
            is_weekend = stay_date.weekday() >= 5
            weekend_boost = 0.12 if is_weekend else -0.06
            event_boost = (signals.event_score - 0.5) * 0.18
            festival_boost = (signals.festival_score - 0.3) * 0.10

            # Deterministic noise so the same date always gives the same result
            import random as _random
            rng = _random.Random(f"pace-{stay_date.isoformat()}-{hotel_id}-{selected_room}")
            noise = rng.uniform(-0.05, 0.05)

            actual_fraction = pickup_fraction * (1.0 + weekend_boost + event_boost + festival_boost + noise)
            actual_fraction = round(min(max(actual_fraction, 0.02), 0.99), 3)
            actual = round(final_rooms * actual_fraction)

            variance = actual - expected

            # Status thresholds are proportional to room count so a 3-room
            # variance on a 12-room suite category isn't the same weight as
            # 3 rooms on a 72-room deluxe category.
            total_rooms = room["total_rooms"]
            threshold = max(round(total_rooms * 0.05), 2)   # 5% of inventory, min 2

            if variance <= -threshold:
                status = "behind"
            elif variance >= threshold:
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
                    variance=variance,
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

    # Dynamic confidence — penalised by booking window (far-out = uncertain),
    # extreme price swings, and low demand signal strength; rewarded by
    # stable pace and strong demand.
    days_until = max((stay_date - date.today()).days, 0)
    booking_window_penalty = min(days_until / 90, 1.0) * 0.10   # up to -10% for 90-day horizon
    swing_penalty = min(abs(total_lift) * 0.25, 0.08)            # up to -8% for large price moves
    pace_bonus = 0.04 if abs(pace.variance) <= 2 else 0.0        # +4% when pace is stable
    demand_score = min(base["market_demand_index"], 0.95) * 0.22 # up to +21% for strong demand
    confidence = round(
        min(max(0.58 + demand_score + pace_bonus - booking_window_penalty - swing_penalty, 0.50), 0.95),
        2,
    )

    # Price direction helper
    price_direction = "raising" if total_lift > 0 else "lowering"
    price_change_pct = abs(total_lift) * 100

    # Occupancy explanation
    occ_vs_target = base["expected_occupancy"] - 0.68
    if occ_vs_target > 0.06:
        occ_detail = (
            f"Forecast occupancy is {base['expected_occupancy']:.0%} — "
            f"{occ_vs_target:.0%} above the 68% target threshold. "
            f"High fill rate supports {price_direction} price by {abs(occupancy_lift) * 100:.1f}%."
        )
    elif occ_vs_target < -0.06:
        occ_detail = (
            f"Forecast occupancy is {base['expected_occupancy']:.0%} — "
            f"{abs(occ_vs_target):.0%} below the 68% target threshold. "
            f"Weak fill rate is pulling price down by {abs(occupancy_lift) * 100:.1f}%."
        )
    else:
        occ_detail = (
            f"Forecast occupancy is {base['expected_occupancy']:.0%}, close to the 68% target. "
            f"Occupancy has a near-neutral effect ({occupancy_lift * 100:+.1f}%) on this recommendation."
        )

    # Booking pace explanation
    if pace.variance > 2:
        pace_detail = (
            f"Bookings are {pace.variance} rooms ahead of expected pace for this date. "
            f"Strong early demand justifies a {pace_lift * 100:.1f}% price uplift."
        )
    elif pace.variance < -2:
        pace_detail = (
            f"Bookings are {abs(pace.variance)} rooms behind expected pace. "
            f"Sluggish pickup is applying a {abs(pace_lift) * 100:.1f}% downward pressure on price."
        )
    else:
        pace_detail = (
            f"Bookings are within {abs(pace.variance)} room(s) of expected pace — on track. "
            f"Pace has a minimal effect ({pace_lift * 100:+.1f}%) on this recommendation."
        )

    # Demand index explanation
    signals = demand_signals(stay_date, hotel_id)
    demand_detail = (
        f"Market demand index is {base['market_demand_index']:.2f}/1.00 "
        f"(event: {signals.event_score:.2f}, festival: {signals.festival_score:.2f}, "
        f"weather: {signals.weather_score:.2f}). "
        f"This is {'above' if base['market_demand_index'] >= 0.55 else 'below'} the 0.55 baseline, "
        f"contributing {demand_lift * 100:+.1f}% to the final price."
    )

    # Competitor explanation
    comp_diff = competitor_avg - current_price
    comp_diff_pct = (comp_diff / current_price) * 100
    if comp_diff > 0:
        comp_detail = (
            f"Competitors average INR {competitor_avg:,.0f} — "
            f"INR {comp_diff:,.0f} ({comp_diff_pct:.1f}%) above our current price of INR {current_price:,.0f}. "
            f"Room to raise: applying a {competitor_lift * 100:.1f}% uplift."
        )
    else:
        comp_detail = (
            f"Competitors average INR {competitor_avg:,.0f} — "
            f"INR {abs(comp_diff):,.0f} ({abs(comp_diff_pct):.1f}%) below our current price of INR {current_price:,.0f}. "
            f"Competitive pressure applying a {abs(competitor_lift) * 100:.1f}% downward adjustment."
        )

    explanations = [
        PricingExplanation(factor="Occupancy forecast", impact=round(occupancy_lift, 3), detail=occ_detail),
        PricingExplanation(factor="Booking pace", impact=round(pace_lift, 3), detail=pace_detail),
        PricingExplanation(factor="Market demand index", impact=round(demand_lift, 3), detail=demand_detail),
        PricingExplanation(factor="Competitor pricing", impact=round(competitor_lift, 3), detail=comp_detail),
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
