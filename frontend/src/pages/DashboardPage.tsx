import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  MapPin,
  Plus,
  Users,
  Calendar,
  TrendingDown,
  LogOut,
  IndianRupee,
  Compass,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { listMyTrips, type TripResponse } from "../api/tripApi";

// ─────────────────────────────────────────────────────────────
// VoyageAI — DashboardPage
// Same design tokens as Login/Register:
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

function TripCard({ trip }: { trip: TripResponse }) {
  const dest =
    trip.end_location && trip.end_location !== trip.start_location
      ? `${trip.start_location} → ${trip.end_location}`
      : trip.start_location;

  return (
    <Link
      to={`/trips/${trip.id}`}
      className="block rounded-2xl p-6 transition-transform duration-200 hover:-translate-y-0.5"
      style={{
        background: "#FBF6EF",
        border: "1px solid #3A322B",
        textDecoration: "none",
      }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-1.5">
          <MapPin size={14} color="#C9683F" />
          <span
            className="text-[11px] uppercase tracking-[0.12em]"
            style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
          >
            {TIER_LABEL[trip.budget_tier] ?? trip.budget_tier}
          </span>
        </div>
        {trip.distance_saved_km != null && trip.distance_saved_km > 0 && (
          <div
            className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full"
            style={{ background: "#EFE6D8", color: "#3F8F5F" }}
          >
            <TrendingDown size={11} />
            {trip.distance_saved_km.toFixed(0)} km saved
          </div>
        )}
      </div>

      <h3
        className="text-xl mb-3 leading-snug"
        style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#241E1A" }}
      >
        {dest}
      </h3>

      <div
        className="flex items-center gap-4 text-sm mb-4"
        style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
      >
        <span className="flex items-center gap-1.5">
          <Calendar size={14} /> {trip.num_days} {trip.num_days === 1 ? "day" : "days"}
        </span>
        <span className="flex items-center gap-1.5">
          <Users size={14} /> {trip.num_travelers}
        </span>
        {trip.total_distance_km != null && (
          <span className="flex items-center gap-1.5">
            <Compass size={14} /> {trip.total_distance_km.toFixed(0)} km
          </span>
        )}
      </div>

      {trip.budget ? (
        <div
          className="flex items-center justify-between pt-3"
          style={{ borderTop: "1px solid #E5DAC8" }}
        >
          <span
            className="text-xs"
            style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
          >
            Estimated budget
          </span>
          <span
            className="flex items-center gap-0.5 text-[15px] font-medium"
            style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}
          >
            <IndianRupee size={13} />
            {Number(trip.budget.total_cost).toLocaleString("en-IN", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </span>
        </div>
      ) : (
        <div
          className="pt-3"
          style={{ borderTop: "1px solid #E5DAC8" }}
        >
          <span
            className="text-xs"
            style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
          >
            Budget not calculated
          </span>
        </div>
      )}
    </Link>
  );
}

function EmptyState() {
  return (
    <div
      className="flex flex-col items-center justify-center text-center py-24 px-6 rounded-2xl"
      style={{ background: "#FBF6EF", border: "1px dashed #DDD0BE" }}
    >
      <div
        className="w-14 h-14 rounded-full flex items-center justify-center mb-5"
        style={{ background: "#F4EEE4" }}
      >
        <Compass size={24} color="#C9683F" />
      </div>
      <h2
        className="text-2xl mb-2"
        style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#241E1A" }}
      >
        No trips yet
      </h2>
      <p
        className="text-sm mb-6 max-w-xs"
        style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
      >
        Plan your first trip and let your Travel Twin handle the route, budget, and
        itinerary.
      </p>
      <Link
        to="/trips/new"
        className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-[15px] font-medium"
        style={{
          background: "#C9683F",
          color: "#FBF6EF",
          fontFamily: "Inter, sans-serif",
          textDecoration: "none",
        }}
      >
        <Plus size={16} /> Plan your first trip
      </Link>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="rounded-2xl p-6 h-[190px] animate-pulse"
          style={{ background: "#2E2620" }}
        />
      ))}
    </div>
  );
}

export function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const {
    data: trips,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["trips"],
    queryFn: listMyTrips,
  });

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const firstName = user?.full_name?.split(" ")[0] ?? "there";

  return (
    <div className="min-h-screen w-full" style={{ background: "#241E1A" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');
      `}</style>

      {/* Top bar */}
      <header
        className="flex items-center justify-between px-6 sm:px-10 py-5"
        style={{ borderBottom: "1px solid #3A322B" }}
      >
        <div className="flex items-center gap-1.5">
          <MapPin size={16} color="#C9683F" />
          <span
            className="text-sm uppercase tracking-[0.14em]"
            style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
          >
            VoyageAI
          </span>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 text-sm"
          style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
        >
          <LogOut size={15} /> Log out
        </button>
      </header>

      <main className="max-w-5xl mx-auto px-6 sm:px-10 py-10">
        <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <div>
            <h1
              className="text-[32px] leading-tight mb-1"
              style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#F4EEE4" }}
            >
              Welcome back, {firstName}
            </h1>
            <p
              className="text-sm"
              style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
            >
              {trips && trips.length > 0
                ? `${trips.length} ${trips.length === 1 ? "trip" : "trips"} planned`
                : "Ready to plan your next journey?"}
            </p>
          </div>
          {trips && trips.length > 0 && (
            <Link
              to="/trips/new"
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-[15px] font-medium"
              style={{
                background: "#C9683F",
                color: "#FBF6EF",
                fontFamily: "Inter, sans-serif",
                textDecoration: "none",
              }}
            >
              <Plus size={16} /> New trip
            </Link>
          )}
        </div>

        {isLoading && <LoadingSkeleton />}

        {isError && (
          <p style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}>
            Couldn't load your trips. Try refreshing the page.
          </p>
        )}

        {!isLoading && !isError && trips && trips.length === 0 && <EmptyState />}

        {!isLoading && !isError && trips && trips.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {trips.map((trip) => (
              <TripCard key={trip.id} trip={trip} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}