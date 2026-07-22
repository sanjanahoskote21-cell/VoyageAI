import React, { useState, useMemo } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Check, Eye, EyeOff, ArrowRight, ArrowLeft, MapPin } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { registerUser } from "../api/authApi";
import { getErrorMessage } from "../utils/getErrorMessage";

// ─────────────────────────────────────────────────────────────
// VoyageAI — RegisterPage
// Design tokens (matches existing LoginPage system):
//   bg:       #241E1A  (warm charcoal)
//   card:     #FBF6EF  (cream)
//   accent:   #C9683F  (terracotta)
//   accent-2: #E3A876  (soft amber, for secondary states)
//   text-hi:  #F4EEE4
//   text-lo:  #A99C8C
// Display face: Fraunces · Body/UI face: Inter
// ─────────────────────────────────────────────────────────────

const CITIES = [
  { name: "Bengaluru", x: 60, y: 72 },
  { name: "Mysore", x: 40, y: 71 },
  { name: "Coorg", x: 20, y: 72 },
  { name: "Mangalore", x: 10, y: 50 },
  { name: "Chikkamagalur", x: 28, y: 48 },
  { name: "Hampi", x: 35, y: 35 },
  { name: "Dharwad", x: 64, y: 32 },
  { name: "Bidar", x: 78, y: 50 },
];

const ROUTE = "Bidar-Dharwad-Hampi-Chikkamagalur-Mangalore-Coorg-Mysore-Bengaluru"
  .split("-")
  .map((n) => CITIES.find((c) => c.name === n));

function RouteMap() {
  const points = ROUTE.map((c) => `${c.x},${c.y}`).join(" ");
  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid slice"
      className="absolute inset-0 w-full h-full"
      style={{ opacity: 0.58 }}
    >
      <polyline
        points={points}
        fill="none"
        stroke="#6b5579"
        strokeWidth="0.35"
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength="100"
        style={{
          strokeDasharray: 100,
          strokeDashoffset: 100,
          animation: "draw-route 6s ease-in-out infinite",
        }}
      />
      {ROUTE.map((c, i) => (
        <circle
          key={c.name}
          cx={c.x}
          cy={c.y}
          r={i === 0 || i === ROUTE.length - 1 ? 1.1 : 0.7}
          fill={i === ROUTE.length - 1 ? "#E3A876" : "#8B7A66"}
          style={{
            opacity: 0,
            animation: `city-pop 6s ease-in-out infinite`,
            animationDelay: `${(i / ROUTE.length) * 5.5}s`,
          }}
        />
      ))}
      {ROUTE.map((c, i) => (
        <text
          key={`${c.name}-label`}
          x={c.x}
          y={c.y - 2}
          fontSize="2.2"
          textAnchor="middle"
          fill="#F4EEE4"
          style={{
            fontFamily: "Inter, sans-serif",
            opacity: 0,
            animation: `city-pop 6s ease-in-out infinite`,
            animationDelay: `${(i / ROUTE.length) * 5.5}s`,
          }}
        >
          {c.name}
        </text>
      ))}
      <style>{`
        @keyframes draw-route {
          0% { stroke-dashoffset: 100; }
          55% { stroke-dashoffset: 0; }
          85% { stroke-dashoffset: 0; opacity: 0.55; }
          92% { opacity: 0; }
          100% { stroke-dashoffset: 100; opacity: 0; }
        }
        @keyframes city-pop {
          0% { opacity: 0; }
          8% { opacity: 1; }
          85% { opacity: 1; }
          92% { opacity: 0; }
          100% { opacity: 0; }
        }
      `}</style>
    </svg>
  );
}

function passwordStrength(pw) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score; // 0-4
}

const STRENGTH_LABEL = ["Too short", "Weak", "Okay", "Good", "Strong"];

function Field({ label, children }) {
  return (
    <label className="block mb-4">
      <span
        className="block text-[11px] uppercase tracking-[0.12em] mb-1.5"
        style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
      >
        {label}
      </span>
      {children}
    </label>
  );
}

const inputBase = {
  fontFamily: "Inter, sans-serif",
  background: "#F4EEE4",
  border: "1px solid #DDD0BE",
  color: "#241E1A",
};

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [step, setStep] = useState(1);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [touched, setTouched] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const nameValid = name.trim().length > 1;
  const strength = useMemo(() => passwordStrength(password), [password]);
  const pwValid = strength >= 3;
  const matchValid = confirm.length > 0 && confirm === password;

  const canAdvance = nameValid && emailValid;
  const canSubmit = pwValid && matchValid && !submitting;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setSubmitting(true);
    setError("");
    try {
      await registerUser({ email, password, full_name: name });
      await login({ email, password });
      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="min-h-screen w-full relative flex items-center justify-center overflow-hidden px-6"
      style={{ background: "#241E1A" }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');
      `}</style>

      <RouteMap />
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(circle at 50% 45%, rgba(36,30,26,0.15), rgba(36,30,26,0.85) 100%)",
        }}
      />

      {/* Card */}
      <div
        className="relative z-10 w-full max-w-[420px] rounded-2xl p-8 sm:p-10 shadow-2xl"
        style={{ background: "#FBF6EF" }}
      >
        <div className="flex items-center gap-1.5 mb-1.5">
          <MapPin size={14} color="#C9683F" />
          <span
            className="text-[11px] uppercase tracking-[0.14em]"
            style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
          >
            VoyageAI
          </span>
        </div>

        <h1
          className="text-[28px] leading-tight mb-1.5"
          style={{
            fontFamily: "Fraunces, serif",
            fontWeight: 500,
            color: "#241E1A",
          }}
        >
          {step === 1 ? "Start your journey" : "Secure your account"}
        </h1>
        <p
          className="text-sm mb-6"
          style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
        >
          {step === 1
            ? "Plan your first trip with your Travel Twin."
            : "One last step before your first itinerary."}
        </p>

        {/* Progress */}
        <div className="flex gap-1.5 mb-7">
          {[1, 2].map((s) => (
            <div
              key={s}
              className="h-[3px] flex-1 rounded-full transition-colors duration-300"
              style={{ background: s <= step ? "#C9683F" : "#E5DAC8" }}
            />
          ))}
        </div>

        {step === 1 && (
          <div>
            <Field label="Full name">
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ananya Rao"
                className="w-full px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
                style={{ ...inputBase, "--tw-ring-color": "#C9683F" }}
              />
            </Field>
            <Field label="Email">
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onBlur={() => setTouched(true)}
                  placeholder="you@example.com"
                  className="w-full px-3.5 py-2.5 pr-9 rounded-lg text-[15px] outline-none focus:ring-2"
                  style={inputBase}
                />
                {email.length > 0 && (
                  <span className="absolute right-3 top-1/2 -translate-y-1/2">
                    {emailValid ? (
                      <Check size={16} color="#3F8F5F" />
                    ) : (
                      <span
                        className="block w-1.5 h-1.5 rounded-full"
                        style={{ background: "#C9683F" }}
                      />
                    )}
                  </span>
                )}
              </div>
              {touched && !emailValid && email.length > 0 && (
                <span
                  className="block text-xs mt-1"
                  style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
                >
                  Enter a valid email address
                </span>
              )}
            </Field>

            <button
              disabled={!canAdvance}
              onClick={() => setStep(2)}
              className="w-full mt-2 flex items-center justify-center gap-2 py-3 rounded-lg text-[15px] font-medium transition-all duration-200"
              style={{
                fontFamily: "Inter, sans-serif",
                background: canAdvance ? "#C9683F" : "#E5DAC8",
                color: canAdvance ? "#FBF6EF" : "#A99C8C",
                cursor: canAdvance ? "pointer" : "not-allowed",
              }}
            >
              Continue <ArrowRight size={16} />
            </button>
          </div>
        )}

        {step === 2 && (
          <div>
            <Field label="Password">
              <div className="relative">
                <input
                  type={showPw ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 pr-10 rounded-lg text-[15px] outline-none focus:ring-2"
                  style={inputBase}
                />
                <button
                  type="button"
                  onClick={() => setShowPw((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  style={{ color: "#A99C8C" }}
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>

              {password.length > 0 && (
                <div className="mt-2">
                  <div className="flex gap-1">
                    {[0, 1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className="h-1 flex-1 rounded-full transition-colors duration-200"
                        style={{
                          background:
                            i < strength
                              ? strength >= 3
                                ? "#3F8F5F"
                                : "#C9683F"
                              : "#E5DAC8",
                        }}
                      />
                    ))}
                  </div>
                  <span
                    className="block text-xs mt-1"
                    style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
                  >
                    {STRENGTH_LABEL[strength]} — use 8+ chars, a number, and a symbol
                  </span>
                </div>
              )}
            </Field>

            <Field label="Confirm password">
              <div className="relative">
                <input
                  type={showPw ? "text" : "password"}
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 pr-9 rounded-lg text-[15px] outline-none focus:ring-2"
                  style={inputBase}
                />
                {confirm.length > 0 && (
                  <span className="absolute right-3 top-1/2 -translate-y-1/2">
                    {matchValid ? (
                      <Check size={16} color="#3F8F5F" />
                    ) : (
                      <span
                        className="block w-1.5 h-1.5 rounded-full"
                        style={{ background: "#C9683F" }}
                      />
                    )}
                  </span>
                )}
              </div>
            </Field>

            {error && (
              <p
                className="text-sm mb-3"
                style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
              >
                {error}
              </p>
            )}

            <div className="flex gap-2 mt-2">
              <button
                onClick={() => setStep(1)}
                className="flex items-center justify-center gap-1.5 px-4 py-3 rounded-lg text-sm"
                style={{
                  fontFamily: "Inter, sans-serif",
                  background: "transparent",
                  border: "1px solid #DDD0BE",
                  color: "#8B7A66",
                }}
              >
                <ArrowLeft size={15} /> Back
              </button>
              <button
                disabled={!canSubmit}
                onClick={handleSubmit}
                className="flex-1 py-3 rounded-lg text-[15px] font-medium transition-all duration-200"
                style={{
                  fontFamily: "Inter, sans-serif",
                  background: canSubmit ? "#C9683F" : "#E5DAC8",
                  color: canSubmit ? "#FBF6EF" : "#A99C8C",
                  cursor: canSubmit ? "pointer" : "not-allowed",
                }}
              >
                {submitting ? "Creating account..." : "Create account"}
              </button>
            </div>
          </div>
        )}

        <p
          className="text-center text-sm mt-6"
          style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
        >
          Already have an account?{" "}
          <Link to="/login" style={{ color: "#C9683F" }}>
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}