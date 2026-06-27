from app.schemas.revenue import ForecastRequest, PriceRecommendationRequest
from app.services.revenue_intelligence import dashboard, forecast, recommend_price


def test_forecast_respects_horizon():
    points = forecast(ForecastRequest(horizon_days=7, room_type="Deluxe"))

    assert len(points) == 7
    assert all(0 < point.expected_occupancy <= 1 for point in points)


def test_recommendation_has_explanations():
    recommendation = recommend_price(PriceRecommendationRequest(room_type="Suite"))

    assert recommendation.recommended_price > 0
    assert recommendation.confidence_score > 0
    assert len(recommendation.explanations) >= 4


def test_dashboard_summary_contains_core_metrics():
    summary = dashboard()

    assert summary.revenue_forecast > 0
    assert summary.occupancy_forecast > 0
    assert summary.recommendations
    assert len(summary.hotels) >= 4
    assert summary.channel_mix
    assert summary.segment_performance


def test_dashboard_filters_hotel_room_and_horizon():
    summary = dashboard(hotel_id="HRI-GOA-002", room_type="Suite", horizon_days=14)

    assert summary.selected_hotel_id == "HRI-GOA-002"
    assert summary.selected_room_type == "Suite"
    assert summary.horizon_days == 14
    assert len(summary.forecast) == 14
    assert all(point.city == "Goa" for point in summary.forecast)
