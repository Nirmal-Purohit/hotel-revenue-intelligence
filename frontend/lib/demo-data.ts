import type { DashboardSummary, HotelOption, RoomType } from "./types";

const hotels: HotelOption[] = [
  { hotel_id: "HRI-BLR-001", property_name: "Aster Regency Bengaluru", city: "Bengaluru", star_rating: 4.3, room_types: ["Deluxe", "Executive", "Suite", "Premium", "Family"] },
  { hotel_id: "HRI-GOA-002", property_name: "Casa Marina Goa", city: "Goa", star_rating: 4.6, room_types: ["Deluxe", "Executive", "Suite", "Premium", "Family"] },
  { hotel_id: "HRI-JAI-003", property_name: "Rang Mahal Jaipur", city: "Jaipur", star_rating: 4.1, room_types: ["Deluxe", "Executive", "Suite", "Premium", "Family"] },
  { hotel_id: "HRI-MUM-004", property_name: "Harbor View Mumbai", city: "Mumbai", star_rating: 4.4, room_types: ["Deluxe", "Executive", "Suite", "Premium", "Family"] }
];

const rooms: RoomType[] = ["Deluxe", "Executive", "Suite", "Premium", "Family"];
const basePrice: Record<RoomType, number> = { Deluxe: 5200, Executive: 7100, Suite: 11800, Premium: 8500, Family: 7600 };

const dates = Array.from({ length: 60 }, (_, index) => {
  const date = new Date();
  date.setDate(date.getDate() + index + 1);
  return date.toISOString().slice(0, 10);
});

export const demoDashboard: DashboardSummary = {
  selected_hotel_id: "HRI-BLR-001",
  selected_room_type: null,
  horizon_days: 30,
  hotels,
  revenue_forecast: 29850000,
  occupancy_forecast: 0.76,
  adr: 7280,
  revpar: 5530,
  revenue_opportunity: 742000,
  high_demand_dates: dates.slice(4, 12),
  low_demand_dates: dates.slice(38, 45),
  forecast: dates.flatMap((stay_date, index) =>
    rooms.map((room_type) => {
      const demand = 0.45 + ((index % 11) / 22);
      const adr = basePrice[room_type] * (0.92 + demand * 0.34);
      const roomsSold = room_type === "Suite" ? 10 : room_type === "Executive" ? 28 : room_type === "Family" ? 17 : 48;
      return {
        stay_date,
        hotel_id: "HRI-BLR-001",
        property_name: "Aster Regency Bengaluru",
        city: "Bengaluru",
        room_type,
        expected_occupancy: Math.min(0.95, demand),
        expected_rooms_sold: roomsSold,
        expected_revenue: Math.round(roomsSold * adr),
        adr: Math.round(adr),
        revpar: Math.round(adr * demand),
        market_demand_index: Number(demand.toFixed(2))
      };
    })
  ),
  booking_pace: dates.slice(0, 30).flatMap((stay_date, index) =>
    rooms.map((room_type) => ({
      stay_date,
      hotel_id: "HRI-BLR-001",
      property_name: "Aster Regency Bengaluru",
      city: "Bengaluru",
      room_type,
      actual_bookings: 18 + index + (room_type === "Suite" ? -9 : 0),
      expected_bookings: 17 + index,
      variance: index % 5 === 0 ? -4 : index % 4,
      status: index % 5 === 0 ? "behind" : index % 3 === 0 ? "ahead" : "on_track"
    }))
  ),
  recommendations: dates.slice(0, 14).flatMap((stay_date, index) =>
    rooms.map((room_type) => ({
      stay_date,
      hotel_id: "HRI-BLR-001",
      property_name: "Aster Regency Bengaluru",
      city: "Bengaluru",
      room_type,
      current_price: basePrice[room_type],
      recommended_price: Math.round(basePrice[room_type] * (1.02 + index / 80)),
      suggested_change: Math.round(basePrice[room_type] * (0.02 + index / 80)),
      expected_occupancy: 0.66 + index / 50,
      expected_revenue: Math.round(basePrice[room_type] * (10 + index)),
      confidence_score: 0.78,
      explanations: [
        { factor: "Occupancy forecast", impact: 0.04, detail: "Demand is above the normal booking curve." },
        { factor: "Competitor pricing", impact: 0.02, detail: "Comparable hotels are pricing above current ADR." }
      ]
    }))
  ),
  channel_mix: [
    { channel: "OTA", bookings: 1240, revenue: 8800000, share: 0.38 },
    { channel: "Direct", bookings: 820, revenue: 7100000, share: 0.27 },
    { channel: "Corporate", bookings: 630, revenue: 4300000, share: 0.2 },
    { channel: "Travel Agent", bookings: 310, revenue: 2100000, share: 0.1 },
    { channel: "Walk-in", bookings: 160, revenue: 1250000, share: 0.05 }
  ],
  segment_performance: [
    { segment: "Business", bookings: 1060, adr: 7450, cancellation_rate: 0.08 },
    { segment: "Leisure", bookings: 970, adr: 7820, cancellation_rate: 0.12 },
    { segment: "Family", bookings: 500, adr: 6900, cancellation_rate: 0.1 },
    { segment: "Group", bookings: 340, adr: 6320, cancellation_rate: 0.16 },
    { segment: "International", bookings: 250, adr: 8460, cancellation_rate: 0.09 }
  ]
};
