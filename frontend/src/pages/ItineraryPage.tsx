import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  MapPin,
  Calendar,
  Users,
  Car,
  TrendingDown,
  Compass,
  MessageCircle,
} from "lucide-react";
import { getTrip } from "../api/tripApi";

// ─────────────────────────────────────────────────────────────
// VoyageAI — ItineraryPage
// Same design tokens as Login/Register/Dashboard/TripPlanner:
//   bg: #241E1A (charcoal) · card: #FBF6EF (cream)
//   accent: #C9683F (terracotta) · accent-2: #E3A876 (amber)
//   text-hi: #F4EEE4 · text-lo: #A99C8C
//   Display: Fraunces · Body/UI: Inter
// ─────────────────────────────────────────────────────────────

const TIER_LABEL: Record<string, string> = {
  budget: "Budget",
  mid: "Mid-range",
  luxury: "Luxury",
};

const MODE_LABEL: Record<string, string> = {
  car: "Car",
  bike: "Bike",
  public_transport: "Public transport",
};

function money(value: number | string) {
  return Number(value).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function StatusScreen({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="min-h-screen w-full flex items-center justify-center"
      style={{ background: "#241E1A" }}
    >
      <p style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}>{children}</p>
    </div>
  );
}

export function ItineraryPage() {
  const { tripId } = useParams<{ tripId: string }>();
  const {
    data: trip,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["trip", tripId],
    queryFn: () => getTrip(tripId!),
    enabled: !!tripId,
  });

  if (isLoading) return <StatusScreen>Loading your itinerary...</StatusScreen>;
  if (error || !trip) return <StatusScreen>Couldn't load this trip.</StatusScreen>;

  const orderedPlaces = trip.places
    .slice()
    .sort((a, b) => (a.visit_order ?? 0) - (b.visit_order ?? 0));

  return (
    <div className="min-h-screen w-full" style={{ background: "#241E1A" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');
      `}</style>

      {/* Top bar */}
      <header
        className="flex items-center px-6 sm:px-10 py-5"
        style={{ borderBottom: "1px solid #3A322B" }}
      >
        <Link
          to="/dashboard"
          className="flex items-center gap-1.5 text-sm"
          style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif", textDecoration: "none" }}
        >
          <ArrowLeft size={15} /> Dashboard
        </Link>
      </header>

      <main className="max-w-3xl mx-auto px-6 sm:px-10 py-10">
        <div className="flex items-center gap-1.5 mb-2">
          <MapPin size={14} color="#C9683F" />
          <span
            className="text-[11px] uppercase tracking-[0.14em]"
            style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
          >
            {TIER_LABEL[trip.budget_tier] ?? trip.budget_tier}
          </span>
        </div>

        <h1
          className="text-[32px] leading-tight mb-3"
          style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#F4EEE4" }}
        >
          {trip.start_location}
          {trip.end_location && trip.end_location !== trip.start_location
            ? ` → ${trip.end_location}`
            : ""}
        </h1>

        <div
          className="flex flex-wrap items-center gap-4 text-sm mb-8"
          style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
        >
          <span className="flex items-center gap-1.5">
            <Calendar size={14} /> {trip.num_days} {trip.num_days === 1 ? "day" : "days"}
          </span>
          <span className="flex items-center gap-1.5">
            <Users size={14} /> {trip.num_travelers}{" "}
            {trip.num_travelers === 1 ? "traveler" : "travelers"}
          </span>
          <span className="flex items-center gap-1.5">
            <Car size={14} /> {MODE_LABEL[trip.travel_mode] ?? trip.travel_mode}
          </span>
        </div>

        {trip.total_distance_km != null && (
          <div
            className="flex items-center gap-3 rounded-2xl px-5 py-4 mb-8"
            style={{ background: "#2E2620" }}
          >
            <Compass size={18} color="#C9683F" />
            <p
              className="text-sm"
              style={{ color: "#F4EEE4", fontFamily: "Inter, sans-serif" }}
            >
              {Number(trip.total_distance_km).toFixed(0)} km total route
            </p>
            {trip.distance_saved_km != null && trip.distance_saved_km > 0 && (
              <span
                className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full ml-auto"
                style={{ background: "#3A3226", color: "#3FA86A" }}
              >
                <TrendingDown size={11} />
                {Number(trip.distance_saved_km).toFixed(0)} km saved via optimization
              </span>
            )}
          </div>
        )}

        {/* Places */}
        <h2
          className="text-lg mb-3"
          style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#F4EEE4" }}
        >
          Places
        </h2>
        <div className="grid gap-2 mb-8">
          {orderedPlaces.map((place, i) => (
            <div
              key={place.id}
              className="flex items-center gap-3 rounded-xl px-4 py-3"
              style={{ background: "#FBF6EF" }}
            >
              <span
                className="flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium shrink-0"
                style={{ background: "#EFE6D8", color: "#C9683F" }}
              >
                {i + 1}
              </span>
              <div>
                <p
                  className="text-[15px] font-medium"
                  style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}
                >
                  {place.display_name}
                </p>
                {place.display_city && (
                  <p
                    className="text-sm"
                    style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
                  >
                    {place.display_city}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Budget */}
        {trip.budget && (
          <>
            <h2
              className="text-lg mb-3"
              style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#F4EEE4" }}
            >
              Budget
            </h2>
            <div
              className="rounded-2xl p-6 mb-8"
              style={{ background: "#FBF6EF" }}
            >
              {[
                ["Hotel", trip.budget.hotel_cost],
                ["Food", trip.budget.food_cost],
                ["Fuel", trip.budget.fuel_cost],
                ["Misc", trip.budget.misc_cost],
              ].map(([label, value]) => (
                <div
                  key={label as string}
                  className="flex items-center justify-between py-2"
                >
                  <span
                    className="text-sm"
                    style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
                  >
                    {label}
                  </span>
                  <span
                    className="text-[15px]"
                    style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}
                  >
                    ₹{money(value as number)}
                  </span>
                </div>
              ))}
              <div
                className="flex items-center justify-between pt-3 mt-2"
                style={{ borderTop: "1px solid #E5DAC8" }}
              >
                <span
                  className="text-[15px] font-medium"
                  style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}
                >
                  Total
                </span>
                <span
                  className="text-lg font-medium"
                  style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
                >
                  ₹{money(trip.budget.total_cost)}
                </span>
              </div>
            </div>
          </>
        )}

        <Link
          to={`/trips/${trip.id}/chat`}
          className="inline-flex items-center gap-2 px-5 py-3 rounded-lg text-[15px] font-medium"
          style={{
            background: "#C9683F",
            color: "#FBF6EF",
            fontFamily: "Inter, sans-serif",
            textDecoration: "none",
          }}
        >
          <MessageCircle size={16} /> Chat with Travel Twin
        </Link>
      </main>
    </div>
  );
}