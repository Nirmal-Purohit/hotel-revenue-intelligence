from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, timedelta


ROOM_TYPES = ["Deluxe", "Executive", "Suite", "Premium", "Family"]

HOTELS = {
    "HRI-BLR-001": {
        "property_name": "Aster Regency Bengaluru",
        "city": "Bengaluru",
        "star_rating": 4.3,
        "demand_bias": 0.05,
        "rooms": {
            "Deluxe": {"total_rooms": 72, "base_price": 5200},
            "Executive": {"total_rooms": 38, "base_price": 7100},
            "Suite": {"total_rooms": 14, "base_price": 11800},
            "Premium": {"total_rooms": 26, "base_price": 8500},
            "Family": {"total_rooms": 20, "base_price": 7600},
        },
    },
    "HRI-GOA-002": {
        "property_name": "Casa Marina Goa",
        "city": "Goa",
        "star_rating": 4.6,
        "demand_bias": 0.11,
        "rooms": {
            "Deluxe": {"total_rooms": 54, "base_price": 6800},
            "Executive": {"total_rooms": 24, "base_price": 8200},
            "Suite": {"total_rooms": 18, "base_price": 15600},
            "Premium": {"total_rooms": 32, "base_price": 10400},
            "Family": {"total_rooms": 30, "base_price": 9800},
        },
    },
    "HRI-JAI-003": {
        "property_name": "Rang Mahal Jaipur",
        "city": "Jaipur",
        "star_rating": 4.1,
        "demand_bias": 0.02,
        "rooms": {
            "Deluxe": {"total_rooms": 64, "base_price": 4700},
            "Executive": {"total_rooms": 28, "base_price": 6400},
            "Suite": {"total_rooms": 12, "base_price": 10200},
            "Premium": {"total_rooms": 22, "base_price": 7600},
            "Family": {"total_rooms": 18, "base_price": 6900},
        },
    },
    "HRI-MUM-004": {
        "property_name": "Harbor View Mumbai",
        "city": "Mumbai",
        "star_rating": 4.4,
        "demand_bias": 0.08,
        "rooms": {
            "Deluxe": {"total_rooms": 82, "base_price": 7400},
            "Executive": {"total_rooms": 46, "base_price": 9800},
            "Suite": {"total_rooms": 16, "base_price": 17800},
            "Premium": {"total_rooms": 36, "base_price": 12600},
            "Family": {"total_rooms": 16, "base_price": 10800},
        },
    },
}

COMPETITORS = {
    "Bengaluru": [("Orchid Grand", 4.2, 0.96), ("The Meridian Court", 4.5, 1.08), ("Azure Residency", 4.1, 0.91), ("Cedar Park Hotel", 4.4, 1.03)],
    "Goa": [("Bay Pearl Resort", 4.5, 1.12), ("Palm Cove Suites", 4.7, 1.18), ("Sunset Bay Hotel", 4.2, 0.98), ("Marina Sands", 4.4, 1.06)],
    "Jaipur": [("Raj Palace Inn", 4.1, 0.94), ("Amber Court", 4.3, 1.04), ("Pink City Residency", 3.9, 0.86), ("Hawa Mahal Suites", 4.5, 1.1)],
    "Mumbai": [("Sea Link Grand", 4.6, 1.14), ("Nariman House Hotel", 4.4, 1.08), ("Metro Bay Residency", 4.0, 0.92), ("Colaba Crest", 4.3, 1.02)],
}

CHANNELS = {
    "OTA": {"share": 0.38, "adr_multiplier": 0.97},
    "Direct": {"share": 0.27, "adr_multiplier": 1.04},
    "Corporate": {"share": 0.2, "adr_multiplier": 0.93},
    "Travel Agent": {"share": 0.1, "adr_multiplier": 0.9},
    "Walk-in": {"share": 0.05, "adr_multiplier": 1.08},
}

SEGMENTS = {
    "Business": {"share": 0.34, "adr_multiplier": 1.02, "cancel": 0.08},
    "Leisure": {"share": 0.31, "adr_multiplier": 1.06, "cancel": 0.12},
    "Family": {"share": 0.16, "adr_multiplier": 0.96, "cancel": 0.1},
    "Group": {"share": 0.11, "adr_multiplier": 0.88, "cancel": 0.16},
    "International": {"share": 0.08, "adr_multiplier": 1.14, "cancel": 0.09},
}

CITY_EVENTS = {
    "Bengaluru": ["Tech summit", "Startup week", "Music festival", "Cricket match"],
    "Goa": ["Beach festival", "Long weekend rush", "Wedding season", "New year demand"],
    "Jaipur": ["Literature festival", "Wedding season", "Heritage expo", "Tourism fair"],
    "Mumbai": ["Trade exhibition", "Concert night", "Finance conference", "Film awards"],
}


@dataclass(frozen=True)
class DemandSignals:
    holiday_score: float
    festival_score: float
    weather_score: float
    event_score: float
    competitor_price_index: float
    event_name: str

    @property
    def market_demand_index(self) -> float:
        score = (
            self.holiday_score * 0.22
            + self.festival_score * 0.2
            + self.weather_score * 0.13
            + self.event_score * 0.25
            + self.competitor_price_index * 0.2
        )
        return round(min(max(score, 0.0), 1.0), 3)


def _rng(stay_date: date, hotel_id: str = "", room_type: str = "") -> random.Random:
    return random.Random(f"{stay_date.isoformat()}-{hotel_id}-{room_type}")


def hotel_options() -> list[dict]:
    return [
        {
            "hotel_id": hotel_id,
            "property_name": hotel["property_name"],
            "city": hotel["city"],
            "star_rating": hotel["star_rating"],
            "room_types": list(hotel["rooms"].keys()),
        }
        for hotel_id, hotel in HOTELS.items()
    ]


def rooms_for(hotel_id: str) -> dict:
    return HOTELS[hotel_id]["rooms"]


def demand_signals(stay_date: date, hotel_id: str = "HRI-BLR-001") -> DemandSignals:
    hotel = HOTELS[hotel_id]
    city = hotel["city"]
    rng = _rng(stay_date, hotel_id)
    is_weekend = stay_date.weekday() >= 5
    day_of_year = stay_date.timetuple().tm_yday
    seasonal_wave = (math.sin((day_of_year / 365) * 2 * math.pi - 0.8) + 1) / 2
    winter_or_festival = stay_date.month in {10, 11, 12} or (stay_date.month == 1 and stay_date.day < 10)
    city_event_mod = {"Bengaluru": 0.05, "Goa": 0.12, "Jaipur": 0.08, "Mumbai": 0.07}[city]
    event_spike = 0.78 + city_event_mod if rng.random() > 0.78 else rng.uniform(0.18, 0.58)
    event_name = rng.choice(CITY_EVENTS[city]) if event_spike > 0.7 else "Normal demand"

    return DemandSignals(
        holiday_score=round(0.8 if is_weekend else rng.uniform(0.18, 0.5), 3),
        festival_score=round(rng.uniform(0.66, 0.96) if winter_or_festival else rng.uniform(0.08, 0.42), 3),
        weather_score=round(min(0.98, 0.46 + seasonal_wave * 0.32 + hotel["demand_bias"] + rng.uniform(-0.08, 0.08)), 3),
        event_score=round(min(event_spike, 0.98), 3),
        competitor_price_index=round(rng.uniform(0.68, 1.0), 3),
        event_name=event_name,
    )


def forecast_for(stay_date: date, hotel_id: str, room_type: str) -> dict:
    hotel = HOTELS[hotel_id]
    room = hotel["rooms"][room_type]
    rng = _rng(stay_date, hotel_id, room_type)
    signals = demand_signals(stay_date, hotel_id)
    days_until = max((stay_date - date.today()).days, 0)
    booking_window_effect = max(0.0, 1 - days_until / 150) * 0.13
    weekend_effect = 0.1 if stay_date.weekday() >= 5 else -0.018
    room_effect = {"Deluxe": 0.0, "Executive": -0.02, "Suite": -0.08, "Premium": -0.035, "Family": 0.035}[room_type]
    noise = rng.uniform(-0.04, 0.04)

    occupancy = 0.39 + signals.market_demand_index * 0.43 + hotel["demand_bias"] + weekend_effect + booking_window_effect + room_effect + noise
    occupancy = round(min(max(occupancy, 0.18), 0.97), 3)

    demand_multiplier = 0.83 + signals.market_demand_index * 0.39 + weekend_effect + hotel["demand_bias"] / 2
    adr = round(room["base_price"] * demand_multiplier, 2)
    rooms_sold = round(room["total_rooms"] * occupancy)
    revenue = round(rooms_sold * adr, 2)
    revpar = round(revenue / room["total_rooms"], 2)

    return {
        "stay_date": stay_date,
        "hotel_id": hotel_id,
        "property_name": hotel["property_name"],
        "city": hotel["city"],
        "room_type": room_type,
        "expected_occupancy": occupancy,
        "expected_rooms_sold": rooms_sold,
        "expected_revenue": revenue,
        "adr": adr,
        "revpar": revpar,
        "market_demand_index": signals.market_demand_index,
    }


def date_range(days: int) -> list[date]:
    start = date.today() + timedelta(days=1)
    return [start + timedelta(days=offset) for offset in range(days)]
