"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowPathIcon,
  ArrowTrendingUpIcon,
  BanknotesIcon,
  BuildingOffice2Icon,
  CalendarDaysIcon,
  ChartBarIcon
} from "@heroicons/react/24/outline";
import {
  BookingPaceChart,
  ChannelMixChart,
  DemandChart,
  ForecastChart,
  RoomRevenueChart,
  SegmentPerformanceChart
} from "@/components/dashboard-charts";
import { MetricCard } from "@/components/metric-card";
import { getDashboard } from "@/lib/api";
import { demoDashboard } from "@/lib/demo-data";
import type { DashboardSummary, RoomType } from "@/lib/types";

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0
});

const percent = new Intl.NumberFormat("en-IN", {
  style: "percent",
  maximumFractionDigits: 1
});

const horizons = [7, 30, 60, 90];

export function RevenueDashboard() {
  const [dashboard, setDashboard] = useState<DashboardSummary>(demoDashboard);
  const [hotelId, setHotelId] = useState(demoDashboard.selected_hotel_id);
  const [roomType, setRoomType] = useState<RoomType | "All">("All");
  const [horizonDays, setHorizonDays] = useState(30);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>("Demo data");

  const selectedHotel = useMemo(
    () => dashboard.hotels.find((hotel) => hotel.hotel_id === hotelId) ?? dashboard.hotels[0],
    [dashboard.hotels, hotelId]
  );

  useEffect(() => {
    let isActive = true;
    setIsLoading(true);
    getDashboard({ hotelId, roomType, horizonDays })
      .then((data) => {
        if (!isActive) return;
        setDashboard(data);
        setLastUpdated(new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }));
      })
      .finally(() => {
        if (isActive) setIsLoading(false);
      });

    return () => {
      isActive = false;
    };
  }, [hotelId, roomType, horizonDays]);

  const topRecommendations = dashboard.recommendations
    .slice()
    .sort((a, b) => b.suggested_change - a.suggested_change)
    .slice(0, 10);
  const focusRecommendation = topRecommendations[0];
  const behindPaceCount = dashboard.booking_pace.filter((point) => point.status === "behind").length;
  const totalBookings = dashboard.channel_mix.reduce((sum, point) => sum + point.bookings, 0);

  return (
    <main className="min-h-screen">
      <header className="border-b border-ink/10 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm font-medium uppercase text-moss">Revenue command center</p>
              <h1 className="mt-1 text-3xl font-semibold tracking-normal text-ink">Hotel Revenue Intelligence</h1>
            </div>
            <div className="flex items-center gap-2 text-sm text-ink/65">
              <ArrowPathIcon className={`h-5 w-5 ${isLoading ? "animate-spin text-ocean" : "text-moss"}`} />
              <span>Updated {lastUpdated}</span>
            </div>
          </div>

          <div className="grid gap-3 rounded-lg border border-ink/10 bg-mist p-3 md:grid-cols-[1.4fr_1fr_1fr_auto]">
            <label className="text-sm font-medium text-ink">
              Property
              <select
                className="mt-1 h-10 w-full rounded-md border border-ink/15 bg-white px-3 text-sm"
                value={hotelId}
                onChange={(event) => {
                  setHotelId(event.target.value);
                  setRoomType("All");
                }}
              >
                {dashboard.hotels.map((hotel) => (
                  <option key={hotel.hotel_id} value={hotel.hotel_id}>
                    {hotel.property_name} - {hotel.city}
                  </option>
                ))}
              </select>
            </label>

            <label className="text-sm font-medium text-ink">
              Room type
              <select
                className="mt-1 h-10 w-full rounded-md border border-ink/15 bg-white px-3 text-sm"
                value={roomType}
                onChange={(event) => setRoomType(event.target.value as RoomType | "All")}
              >
                <option value="All">All room types</option>
                {selectedHotel?.room_types.map((room) => (
                  <option key={room} value={room}>
                    {room}
                  </option>
                ))}
              </select>
            </label>

            <label className="text-sm font-medium text-ink">
              Forecast horizon
              <select
                className="mt-1 h-10 w-full rounded-md border border-ink/15 bg-white px-3 text-sm"
                value={horizonDays}
                onChange={(event) => setHorizonDays(Number(event.target.value))}
              >
                {horizons.map((days) => (
                  <option key={days} value={days}>
                    {days} days
                  </option>
                ))}
              </select>
            </label>

            <div className="flex items-end">
              <button
                className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-medium text-white"
                onClick={() => setHorizonDays((current) => (current === 30 ? 60 : 30))}
              >
                <ChartBarIcon className="h-5 w-5" />
                Toggle view
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-5 py-6">
        <section className="mb-5 flex flex-col gap-2 rounded-lg border border-ink/10 bg-white p-4 shadow-sm md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <BuildingOffice2Icon className="h-8 w-8 text-moss" />
            <div>
              <p className="text-lg font-semibold text-ink">{selectedHotel?.property_name}</p>
              <p className="text-sm text-ink/65">
                {selectedHotel?.city} - {selectedHotel?.star_rating.toFixed(1)} stars - {roomType === "All" ? "Portfolio view" : `${roomType} room view`}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-ink/65">
            <CalendarDaysIcon className="h-5 w-5" />
            <span>{dashboard.horizon_days}-day demand window</span>
          </div>
        </section>

        <section className="grid metric-grid gap-4">
          <MetricCard label={`${dashboard.horizon_days}-day revenue forecast`} value={currency.format(dashboard.revenue_forecast)} tone="good" />
          <MetricCard label="Forecast occupancy" value={percent.format(dashboard.occupancy_forecast)} />
          <MetricCard label="ADR" value={currency.format(dashboard.adr)} />
          <MetricCard label="RevPAR" value={currency.format(dashboard.revpar)} />
          <MetricCard label="Revenue opportunity" value={currency.format(dashboard.revenue_opportunity)} tone="warn" />
          <MetricCard label="Behind pace alerts" value={String(behindPaceCount)} tone={behindPaceCount ? "warn" : "good"} />
        </section>

        <section className="mt-6 grid gap-5 lg:grid-cols-[1.35fr_0.95fr]">
          <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <BanknotesIcon className="h-5 w-5 text-ocean" />
              <h2 className="text-lg font-semibold">Revenue and Occupancy Forecast</h2>
            </div>
            <ForecastChart data={dashboard.forecast} />
          </div>

          <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <ArrowTrendingUpIcon className="h-5 w-5 text-moss" />
              <h2 className="text-lg font-semibold">Market Demand Index</h2>
            </div>
            <DemandChart data={dashboard.forecast} />
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="font-medium text-ink">High demand</p>
                <p className="mt-1 text-ink/65">{dashboard.high_demand_dates.slice(0, 4).join(", ") || "No spikes"}</p>
              </div>
              <div>
                <p className="font-medium text-ink">Low demand</p>
                <p className="mt-1 text-ink/65">{dashboard.low_demand_dates.slice(0, 4).join(", ") || "No dips"}</p>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-6 grid gap-5 lg:grid-cols-3">
          <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Revenue by Room Type</h2>
            <RoomRevenueChart data={dashboard.forecast} />
          </div>
          <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-sm">
            <h2 className="mb-1 text-lg font-semibold">Channel Mix</h2>
            <p className="text-sm text-ink/60">{totalBookings.toLocaleString("en-IN")} forecast bookings</p>
            <ChannelMixChart data={dashboard.channel_mix} />
          </div>
          <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Segment ADR</h2>
            <SegmentPerformanceChart data={dashboard.segment_performance} />
          </div>
        </section>

        <section className="mt-6 grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
          <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Booking Pace Variance</h2>
            <BookingPaceChart data={dashboard.booking_pace} />
          </div>

          <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">Pricing Recommendations</h2>
            <div className="overflow-x-auto rounded-md border border-ink/10">
              <table className="w-full min-w-[680px] text-left text-sm">
                <thead className="bg-mist text-ink/70">
                  <tr>
                    <th className="px-3 py-2 font-medium">Date</th>
                    <th className="px-3 py-2 font-medium">Room</th>
                    <th className="px-3 py-2 font-medium">Current</th>
                    <th className="px-3 py-2 font-medium">Recommended</th>
                    <th className="px-3 py-2 font-medium">Gain</th>
                    <th className="px-3 py-2 font-medium">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink/10">
                  {topRecommendations.map((item) => (
                    <tr key={`${item.stay_date}-${item.room_type}`} className="bg-white">
                      <td className="px-3 py-3">{item.stay_date}</td>
                      <td className="px-3 py-3">{item.room_type}</td>
                      <td className="px-3 py-3">{currency.format(item.current_price)}</td>
                      <td className="px-3 py-3 font-semibold text-moss">{currency.format(item.recommended_price)}</td>
                      <td className="px-3 py-3 text-coral">{currency.format(item.suggested_change)}</td>
                      <td className="px-3 py-3">{percent.format(item.confidence_score)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {focusRecommendation ? (
          <section className="mt-6 rounded-lg border border-ink/10 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold">Top Recommendation Explanation</h2>
            <p className="mt-1 text-sm text-ink/65">
              {focusRecommendation.stay_date} - {focusRecommendation.room_type} - {currency.format(focusRecommendation.current_price)} to{" "}
              {currency.format(focusRecommendation.recommended_price)}
            </p>
            <div className="mt-4 grid gap-3 md:grid-cols-4">
              {focusRecommendation.explanations.map((item) => (
                <div key={item.factor} className="rounded-md border border-ink/10 bg-mist p-3">
                  <p className="text-sm font-semibold text-ink">{item.factor}</p>
                  <p className="mt-1 text-xs text-ink/65">{item.detail}</p>
                </div>
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </main>
  );
}
