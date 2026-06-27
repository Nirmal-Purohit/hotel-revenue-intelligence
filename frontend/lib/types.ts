export type RoomType = "Deluxe" | "Executive" | "Suite" | "Premium" | "Family";

export type ForecastPoint = {
  stay_date: string;
  hotel_id: string;
  property_name: string;
  city: string;
  room_type: RoomType;
  expected_occupancy: number;
  expected_rooms_sold: number;
  expected_revenue: number;
  adr: number;
  revpar: number;
  market_demand_index: number;
};

export type BookingPacePoint = {
  stay_date: string;
  hotel_id: string;
  property_name: string;
  city: string;
  room_type: RoomType;
  actual_bookings: number;
  expected_bookings: number;
  variance: number;
  status: "ahead" | "on_track" | "behind";
};

export type PriceRecommendation = {
  stay_date: string;
  hotel_id: string;
  property_name: string;
  city: string;
  room_type: RoomType;
  current_price: number;
  recommended_price: number;
  suggested_change: number;
  expected_occupancy: number;
  expected_revenue: number;
  confidence_score: number;
  explanations: { factor: string; impact: number; detail: string }[];
};

export type HotelOption = {
  hotel_id: string;
  property_name: string;
  city: string;
  star_rating: number;
  room_types: RoomType[];
};

export type ChannelMixPoint = {
  channel: string;
  bookings: number;
  revenue: number;
  share: number;
};

export type SegmentPerformancePoint = {
  segment: string;
  bookings: number;
  adr: number;
  cancellation_rate: number;
};

export type DashboardSummary = {
  selected_hotel_id: string;
  selected_room_type: RoomType | null;
  horizon_days: number;
  hotels: HotelOption[];
  revenue_forecast: number;
  occupancy_forecast: number;
  adr: number;
  revpar: number;
  revenue_opportunity: number;
  high_demand_dates: string[];
  low_demand_dates: string[];
  recommendations: PriceRecommendation[];
  booking_pace: BookingPacePoint[];
  forecast: ForecastPoint[];
  channel_mix: ChannelMixPoint[];
  segment_performance: SegmentPerformancePoint[];
};

export type DashboardFilters = {
  hotelId: string;
  roomType?: RoomType | "All";
  horizonDays: number;
};
