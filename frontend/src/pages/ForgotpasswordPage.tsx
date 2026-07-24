import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, MapPin, Check } from "lucide-react";
import { forgotPassword } from "../api/authApi";
import { getErrorMessage } from "../utils/getErrorMessage";

const inputStyle = {
  fontFamily: "Inter, sans-serif",
  background: "#F4EEE4",
  border: "1px solid #DDD0BE",
  color: "#241E1A",
};

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");

  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const handleSubmit = async () => {
    if (!emailValid || submitting) return;
    setSubmitting(true);
    setError("");
    try {
      await forgotPassword({ email });
      setSubmitted(true);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="min-h-screen w-full flex items-center justify-center px-6"
      style={{ background: "#241E1A" }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');
      `}</style>

      <div
        className="w-full max-w-[420px] rounded-2xl p-8 sm:p-10 shadow-2xl"
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

        {!submitted ? (
          <>
            <h1
              className="text-[28px] leading-tight mb-1.5"
              style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#241E1A" }}
            >
              Reset your password
            </h1>
            <p
              className="text-sm mb-6"
              style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
            >
              Enter your email and we'll send you a link to reset it.
            </p>

            <label className="block mb-5">
              <span
                className="block text-[11px] uppercase tracking-[0.12em] mb-1.5"
                style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
              >
                Email
              </span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                placeholder="you@example.com"
                className="w-full px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
                style={inputStyle}
              />
            </label>

            {error && (
              <p
                className="text-sm mb-4"
                style={{ color: "#C9683F", fontFamily: "Inter, sans-serif" }}
              >
                {error}
              </p>
            )}

            <button
              disabled={!emailValid || submitting}
              onClick={handleSubmit}
              className="w-full py-3 rounded-lg text-[15px] font-medium transition-all duration-200"
              style={{
                fontFamily: "Inter, sans-serif",
                background: emailValid ? "#C9683F" : "#E5DAC8",
                color: emailValid ? "#FBF6EF" : "#A99C8C",
                cursor: emailValid ? "pointer" : "not-allowed",
              }}
            >
              {submitting ? "Sending..." : "Send reset link"}
            </button>
          </>
        ) : (
          <>
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center mb-5"
              style={{ background: "#EFE6D8" }}
            >
              <Check size={20} color="#3F8F5F" />
            </div>
            <h1
              className="text-[26px] leading-tight mb-2"
              style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#241E1A" }}
            >
              Check your email
            </h1>
            <p
              className="text-sm mb-6"
              style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
            >
              If an account exists for <strong>{email}</strong>, a reset link is on its
              way.
            </p>
          </>
        )}

        <Link
          to="/login"
          className="flex items-center gap-1.5 text-sm mt-6"
          style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif", textDecoration: "none" }}
        >
          <ArrowLeft size={14} /> Back to log in
        </Link>
      </div>
    </div>
  );
}