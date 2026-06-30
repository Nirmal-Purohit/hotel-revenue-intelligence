import { demoDashboard } from "./demo-data";
import type { DashboardFilters, DashboardSummary } from "./types";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function getDashboard(filters?: DashboardFilters): Promise<DashboardSummary> {
  const params = new URLSearchParams();
  if (filters?.hotelId) params.set("hotel_id", filters.hotelId);
  if (filters?.roomType && filters.roomType !== "All") params.set("room_type", filters.roomType);
  if (filters?.horizonDays) params.set("horizon_days", String(filters.horizonDays));
  const query = params.size ? `?${params.toString()}` : "";

  try {
    const response = await fetch(`${apiBaseUrl}/api/dashboard${query}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    return response.json();
  } catch {
    return demoDashboard;
  }
}
