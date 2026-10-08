import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, MapPin, Mail, CalendarDays, BadgeCheck, Compass } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { updateProfile } from "../api/authApi";
import { listMyTrips } from "../api/tripApi";

// ─────────────────────────────────────────────────────────────
// VoyageAI — ProfilePage
// Same design tokens as Dashboard/Itinerary:
//   bg: #241E1A (charcoal) · card: #FBF6EF (cream)
//   accent: #C9683F (terracotta) · accent-2: #E3A876 (amber)
//   text-hi: #F4EEE4 · text-lo: #A99C8C
//   Display: Fraunces · Body/UI: Inter
// ─────────────────────────────────────────────────────────────

function formatMemberSince(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-IN", { month: "long", year: "numeric" });
}

export function ProfilePage() {
  const { user, updateUser } = useAuth();
  const queryClient = useQueryClient();

  const [name, setName] = useState(user?.full_name ?? "");
  const [isEditing, setIsEditing] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const { data: trips } = useQuery({
    queryKey: ["trips"],
    queryFn: listMyTrips,
  });

  const saveMutation = useMutation({
    mutationFn: () => updateProfile({ full_name: name.trim() }),
    onMutate: () => setSaveError(null),
    onSuccess: (updated) => {
      updateUser(updated);
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ["trips"] });
    },
    onError: () => setSaveError("Couldn't save that name. Try again."),
  });

  const handleCancel = () => {
    setName(user?.full_name ?? "");
    setIsEditing(false);
    setSaveError(null);
  };

  if (!user) return null;

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

      <main className="max-w-xl mx-auto px-6 sm:px-10 py-10">
        <div className="flex items-center gap-1.5 mb-2">
          <MapPin size={14} color="#C9683F" />
          <span
            className="text-[11px] uppercase tracking-[0.14em]"
            style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
          >
            Your profile
          </span>
        </div>

        <h1
          className="text-[32px] leading-tight mb-8"
          style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#F4EEE4" }}
        >
          {user.full_name}
        </h1>

        <div className="rounded-2xl p-6 mb-6" style={{ background: "#FBF6EF" }}>
          <div className="flex items-center justify-between mb-4">
            <span
              className="text-xs uppercase tracking-[0.1em]"
              style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
            >
              Name
            </span>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="text-sm font-medium"
                style={{ color: "#C9683F", fontFamily: "Inter, sans-serif", background: "transparent", border: "none", cursor: "pointer" }}
              >
                Edit
              </button>
            )}
          </div>

          {isEditing ? (
            <div>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
                className="w-full px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2 mb-3"
                style={{
                  fontFamily: "Inter, sans-serif",
                  background: "#F4EEE4",
                  border: "1px solid #DDD0BE",
                  color: "#241E1A",
                }}
              />
              {saveError && (
                <p className="text-sm mb-3" style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}>
                  {saveError}
                </p>
              )}
              <div className="flex gap-2">
                <button
                  onClick={() => saveMutation.mutate()}
                  disabled={saveMutation.isPending || !name.trim()}
                  className="px-4 py-2 rounded-lg text-sm font-medium"
                  style={{
                    background: "#C9683F",
                    color: "#FBF6EF",
                    fontFamily: "Inter, sans-serif",
                    border: "none",
                    cursor: saveMutation.isPending ? "default" : "pointer",
                    opacity: saveMutation.isPending || !name.trim() ? 0.6 : 1,
                  }}
                >
                  {saveMutation.isPending ? "Saving..." : "Save"}
                </button>
                <button
                  onClick={handleCancel}
                  disabled={saveMutation.isPending}
                  className="px-4 py-2 rounded-lg text-sm"
                  style={{
                    background: "transparent",
                    color: "#8B7A66",
                    border: "1px solid #DDD0BE",
                    fontFamily: "Inter, sans-serif",
                    cursor: saveMutation.isPending ? "default" : "pointer",
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <p className="text-[17px]" style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}>
              {user.full_name}
            </p>
          )}
        </div>

        <div className="rounded-2xl p-6 mb-6" style={{ background: "#FBF6EF" }}>
          <div className="flex items-center gap-3 py-2">
            <Mail size={16} color="#8B7A66" />
            <span className="text-[15px]" style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}>
              {user.email}
            </span>
            {user.is_verified && (
              <span
                className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full ml-auto"
                style={{ background: "#EFE6D8", color: "#3F8F5F" }}
              >
                <BadgeCheck size={11} /> Verified
              </span>
            )}
          </div>
          <div className="flex items-center gap-3 py-2">
            <CalendarDays size={16} color="#8B7A66" />
            <span className="text-[15px]" style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}>
              Member since {formatMemberSince(user.created_at)}
            </span>
          </div>
          <div className="flex items-center gap-3 py-2">
            <Compass size={16} color="#8B7A66" />
            <span className="text-[15px]" style={{ color: "#241E1A", fontFamily: "Inter, sans-serif" }}>
              {trips ? trips.length : "..."} {trips?.length === 1 ? "trip" : "trips"} planned
            </span>
          </div>
        </div>
      </main>
    </div>
  );
}