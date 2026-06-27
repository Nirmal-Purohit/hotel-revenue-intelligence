"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import type { BookingPacePoint, ChannelMixPoint, ForecastPoint, SegmentPerformancePoint } from "@/lib/types";

const palette = ["#1f6f8b", "#597568", "#b58b35", "#c85f4a", "#34495e"];

export function ForecastChart({ data }: { data: ForecastPoint[] }) {
  const daily = Object.values(
    data.reduce<Record<string, { stay_date: string; revenue: number; occupancy: number; count: number }>>(
      (acc, point) => {
        acc[point.stay_date] ??= { stay_date: point.stay_date.slice(5), revenue: 0, occupancy: 0, count: 0 };
        acc[point.stay_date].revenue += point.expected_revenue;
        acc[point.stay_date].occupancy += point.expected_occupancy;
        acc[point.stay_date].count += 1;
        return acc;
      },
      {}
    )
  ).map((point) => ({
    ...point,
    occupancy: Math.round((point.occupancy / point.count) * 100),
    revenue: Math.round(point.revenue / 1000)
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={daily}>
        <CartesianGrid stroke="#dce4df" vertical={false} />
        <XAxis dataKey="stay_date" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Area type="monotone" dataKey="revenue" name="Revenue (k)" stroke="#1f6f8b" fill="#1f6f8b" fillOpacity={0.18} />
        <Line type="monotone" dataKey="occupancy" name="Occupancy %" stroke="#b58b35" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function BookingPaceChart({ data }: { data: BookingPacePoint[] }) {
  const chartData = data.slice(0, 18).map((point) => ({
    stay_date: `${point.stay_date.slice(5)} ${point.room_type}`,
    variance: point.variance
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={chartData}>
        <CartesianGrid stroke="#dce4df" vertical={false} />
        <XAxis dataKey="stay_date" tick={{ fontSize: 11 }} interval={2} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Bar dataKey="variance" fill="#c85f4a" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function DemandChart({ data }: { data: ForecastPoint[] }) {
  const chartData = Object.values(
    data.reduce<Record<string, { stay_date: string; mdi: number; count: number }>>((acc, point) => {
      acc[point.stay_date] ??= { stay_date: point.stay_date.slice(5), mdi: 0, count: 0 };
      acc[point.stay_date].mdi += point.market_demand_index;
      acc[point.stay_date].count += 1;
      return acc;
    }, {})
  )
    .slice(0, 30)
    .map((point) => ({ stay_date: point.stay_date, mdi: Number((point.mdi / point.count).toFixed(3)) }));

  return (
    <ResponsiveContainer width="100%" height={210}>
      <LineChart data={chartData}>
        <CartesianGrid stroke="#dce4df" vertical={false} />
        <XAxis dataKey="stay_date" tick={{ fontSize: 12 }} interval={4} />
        <YAxis tick={{ fontSize: 12 }} domain={[0, 1]} />
        <Tooltip />
        <Line type="monotone" dataKey="mdi" name="Market Demand Index" stroke="#597568" strokeWidth={3} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function RoomRevenueChart({ data }: { data: ForecastPoint[] }) {
  const chartData = Object.values(
    data.reduce<Record<string, { room_type: string; revenue: number; rooms: number }>>((acc, point) => {
      acc[point.room_type] ??= { room_type: point.room_type, revenue: 0, rooms: 0 };
      acc[point.room_type].revenue += point.expected_revenue;
      acc[point.room_type].rooms += point.expected_rooms_sold;
      return acc;
    }, {})
  ).map((point) => ({ ...point, revenue: Math.round(point.revenue / 1000) }));

  return (
    <ResponsiveContainer width="100%" height={230}>
      <BarChart data={chartData}>
        <CartesianGrid stroke="#dce4df" vertical={false} />
        <XAxis dataKey="room_type" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Bar dataKey="revenue" name="Revenue (k)" radius={[4, 4, 0, 0]}>
          {chartData.map((_, index) => (
            <Cell key={index} fill={palette[index % palette.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ChannelMixChart({ data }: { data: ChannelMixPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={230}>
      <PieChart>
        <Pie data={data} dataKey="bookings" nameKey="channel" innerRadius={48} outerRadius={82} paddingAngle={3}>
          {data.map((_, index) => (
            <Cell key={index} fill={palette[index % palette.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function SegmentPerformanceChart({ data }: { data: SegmentPerformancePoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={230}>
      <BarChart data={data}>
        <CartesianGrid stroke="#dce4df" vertical={false} />
        <XAxis dataKey="segment" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Bar dataKey="adr" name="ADR" fill="#597568" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
