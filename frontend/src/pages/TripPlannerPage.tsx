import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  ArrowLeft,
  MapPin,
  Search,
  Plus,
  X,
  Calendar,
  Users,
  Car,
} from "lucide-react";
import { searchPlaces, type PlaceResponse } from "../api/placeApi";
import { createTrip } from "../api/tripApi";

// ─────────────────────────────────────────────────────────────
// VoyageAI — TripPlannerPage
// Same design tokens as Login/Register/Dashboard:
//   bg: #241E1A (charcoal) · card: #FBF6EF (cream)
//   accent: #C9683F (terracotta) · accent-2: #E3A876 (amber)
//   text-hi: #F4EEE4 · text-lo: #A99C8C
//   Display: Fraunces · Body/UI: Inter
// ─────────────────────────────────────────────────────────────

const inputStyle = {
  fontFamily: "Inter, sans-serif",
  background: "#F4EEE4",
  border: "1px solid #DDD0BE",
  color: "#241E1A",
};

function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <span
      className="block text-[11px] uppercase tracking-[0.12em] mb-1.5"
      style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
    >
      {children}
    </span>
  );
}

export function TripPlannerPage() {
  const navigate = useNavigate();

  const [startLocation, setStartLocation] = useState("");
  const [endLocation, setEndLocation] = useState("");
  const [numDays, setNumDays] = useState(3);
  const [numTravelers, setNumTravelers] = useState(1);
  const [budgetTier, setBudgetTier] = useState("mid");
  const [travelMode, setTravelMode] = useState("car");

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<PlaceResponse[]>([]);
  const [selectedPlaces, setSelectedPlaces] = useState<PlaceResponse[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    const results = await searchPlaces(searchQuery);
    setSearchResults(results);
  };

  const addPlace = (place: PlaceResponse) => {
    if (!selectedPlaces.find((p) => p.id === place.id)) {
      setSelectedPlaces((prev) => [...prev, place]);
    }
  };

  const removePlace = (placeId: string) => {
    setSelectedPlaces((prev) => prev.filter((p) => p.id !== placeId));
  };

  const handleSubmit = async () => {
    if (selectedPlaces.length === 0) {
      setError("Add at least one place to your trip.");
      return;
    }
    setError("");
    setIsSubmitting(true);
    try {
      const trip = await createTrip({
        start_location: startLocation,
        end_location: endLocation || undefined,
        num_days: numDays,
        num_travelers: numTravelers,
        budget_tier: budgetTier,
        travel_mode: travelMode,
        places: selectedPlaces.map((p) => ({ place_id: p.id })),
      });
      navigate(`/trips/${trip.id}`);
    } catch {
      setError("Failed to create trip. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

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

      <main className="max-w-2xl mx-auto px-6 sm:px-10 py-10">
        <div className="flex items-center gap-1.5 mb-2">
          <MapPin size={14} color="#C9683F" />
          <span
            className="text-[11px] uppercase tracking-[0.14em]"
            style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
          >
            VoyageAI
          </span>
        </div>
        <h1
          className="text-[32px] leading-tight mb-8"
          style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#F4EEE4" }}
        >
          Plan a new trip
        </h1>

        {error && (
          <p
            className="text-sm mb-4"
            style={{ color: "#E3A876", fontFamily: "Inter, sans-serif" }}
          >
            {error}
          </p>
        )}

        {/* Trip details card */}
        <div
          className="rounded-2xl p-6 sm:p-7 mb-6"
          style={{ background: "#FBF6EF" }}
        >
          <div className="grid grid-cols-2 gap-4">
            <div>
              <FieldLabel>Start location</FieldLabel>
              <input
                value={startLocation}
                onChange={(e) => setStartLocation(e.target.value)}
                placeholder="Bengaluru"
                className="w-full px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
                style={inputStyle}
              />
            </div>
            <div>
              <FieldLabel>End location (optional)</FieldLabel>
              <input
                value={endLocation}
                onChange={(e) => setEndLocation(e.target.value)}
                placeholder="Same as start"
                className="w-full px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
                style={inputStyle}
              />
            </div>
            <div>
              <FieldLabel>
                <span className="inline-flex items-center gap-1">
                  <Calendar size={11} /> Number of days
                </span>
              </FieldLabel>
              <input
                type="number"
                min={1}
                value={numDays}
                onChange={(e) => setNumDays(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
                style={inputStyle}
              />
            </div>
            <div>
              <FieldLabel>
                <span className="inline-flex items-center gap-1">
                  <Users size={11} /> Travelers
                </span>
              </FieldLabel>
              <input
                type="number"
                min={1}
                value={numTravelers}
                onChange={(e) => setNumTravelers(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
                style={inputStyle}
              />
            </div>
            <div>
              <FieldLabel>Budget tier</FieldLabel>
              <select
                value={budgetTier}
                onChange={(e) => setBudgetTier(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
                style={inputStyle}
              >
                <option value="budget">Budget</option>
                <option value="mid">Mid-range</option>
                <option value="luxury">Luxury</option>
              </select>
            </div>
            <div>
              <FieldLabel>
                <span className="inline-flex items-center gap-1">
                  <Car size={11} /> Travel mode
                </span>
              </FieldLabel>
              <select
                value={travelMode}
                onChange={(e) => setTravelMode(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
                style={inputStyle}
              >
                <option value="car">Car</option>
                <option value="bike">Bike</option>
                <option value="public_transport">Public transport</option>
              </select>
            </div>
          </div>
        </div>

        {/* Places search card */}
        <div
          className="rounded-2xl p-6 sm:p-7 mb-6"
          style={{ background: "#FBF6EF" }}
        >
          <h2
            className="text-lg mb-3"
            style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#241E1A" }}
          >
            Add places
          </h2>
          <div className="flex gap-2 mb-4">
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search places (e.g. Coorg, Mysore Palace)"
              className="flex-1 px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
              style={inputStyle}
            />
            <button
              onClick={handleSearch}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium"
              style={{
                background: "#241E1A",
                color: "#F4EEE4",
                fontFamily: "Inter, sans-serif",
              }}
            >
              <Search size={14} /> Search
            </button>
          </div>

          {searchResults.length > 0 && (
            <div className="grid gap-2 mb-2">
              {searchResults.map((place) => (
                <div
                  key={place.id}
                  className="flex justify-between items-center rounded-lg p-3"
                  style={{ background: "#F4EEE4" }}
                >
                  <div>
                    <p
                      className="font-medium text-[15px]"
                      style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}
                    >
                      {place.name}
                    </p>
                    <p
                      className="text-sm"
                      style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
                    >
                      {place.city} · {place.category}
                    </p>
                  </div>
                  <button
                    onClick={() => addPlace(place)}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium"
                    style={{
                      background: "#C9683F",
                      color: "#FBF6EF",
                      fontFamily: "Inter, sans-serif",
                    }}
                  >
                    <Plus size={13} /> Add
                  </button>
                </div>
              ))}
            </div>
          )}

          {selectedPlaces.length > 0 && (
            <>
              <div
                className="mt-4 mb-2 pt-4"
                style={{ borderTop: "1px solid #E5DAC8" }}
              >
                <span
                  className="text-[11px] uppercase tracking-[0.12em]"
                  style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
                >
                  Selected places
                </span>
              </div>
              <div className="grid gap-2">
                {selectedPlaces.map((place) => (
                  <div
                    key={place.id}
                    className="flex justify-between items-center rounded-lg px-3.5 py-2.5"
                    style={{ background: "#F4EEE4" }}
                  >
                    <p
                      className="text-[15px]"
                      style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}
                    >
                      {place.name}{" "}
                      <span style={{ color: "#8B7A66" }}>({place.city})</span>
                    </p>
                    <button
                      onClick={() => removePlace(place.id)}
                      style={{ color: "#C9683F" }}
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="w-full py-3.5 rounded-lg text-[15px] font-medium transition-opacity duration-200"
          style={{
            background: "#C9683F",
            color: "#FBF6EF",
            fontFamily: "Inter, sans-serif",
            opacity: isSubmitting ? 0.6 : 1,
          }}
        >
          {isSubmitting ? "Creating trip..." : "Create trip"}
        </button>
      </main>
    </div>
  );
}