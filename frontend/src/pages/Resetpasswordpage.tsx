import { useState, useMemo } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { Check, Eye, EyeOff, MapPin, ArrowLeft } from "lucide-react";
import { resetPassword } from "../api/authApi";
import { getErrorMessage } from "../utils/getErrorMessage";

function passwordStrength(pw: string) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score;
}

const STRENGTH_LABEL = ["Too short", "Weak", "Okay", "Good", "Strong"];

const inputStyle = {
  fontFamily: "Inter, sans-serif",
  background: "#F4EEE4",
  border: "1px solid #DDD0BE",
  color: "#241E1A",
};

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  const strength = useMemo(() => passwordStrength(password), [password]);
  const pwValid = strength >= 3;
  const matchValid = confirm.length > 0 && confirm === password;
  const canSubmit = pwValid && matchValid && !!token && !submitting;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setSubmitting(true);
    setError("");
    try {
      await resetPassword({ token, new_password: password });
      setDone(true);
      setTimeout(() => navigate("/login"), 2000);
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

        {!token ? (
          <>
            <h1
              className="text-[26px] leading-tight mb-2"
              style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#241E1A" }}
            >
              Invalid link
            </h1>
            <p
              className="text-sm mb-6"
              style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
            >
              This reset link is missing its token. Request a new one below.
            </p>
            <Link
              to="/forgot-password"
              className="inline-block px-5 py-2.5 rounded-lg text-[15px] font-medium"
              style={{ background: "#C9683F", color: "#FBF6EF", fontFamily: "Inter, sans-serif", textDecoration: "none" }}
            >
              Request new link
            </Link>
          </>
        ) : done ? (
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
              Password updated
            </h1>
            <p
              className="text-sm"
              style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
            >
              Taking you to log in...
            </p>
          </>
        ) : (
          <>
            <h1
              className="text-[28px] leading-tight mb-1.5"
              style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#241E1A" }}
            >
              Set a new password
            </h1>
            <p
              className="text-sm mb-6"
              style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
            >
              This link expires 15 minutes after it was requested.
            </p>

            <label className="block mb-4">
              <span
                className="block text-[11px] uppercase tracking-[0.12em] mb-1.5"
                style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
              >
                New password
              </span>
              <div className="relative">
                <input
                  type={showPw ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 pr-10 rounded-lg text-[15px] outline-none focus:ring-2"
                  style={inputStyle}
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
                            i < strength ? (strength >= 3 ? "#3F8F5F" : "#C9683F") : "#E5DAC8",
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
            </label>

            <label className="block mb-5">
              <span
                className="block text-[11px] uppercase tracking-[0.12em] mb-1.5"
                style={{ color: "#A99C8C", fontFamily: "Inter, sans-serif" }}
              >
                Confirm new password
              </span>
              <div className="relative">
                <input
                  type={showPw ? "text" : "password"}
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 pr-9 rounded-lg text-[15px] outline-none focus:ring-2"
                  style={inputStyle}
                />
                {confirm.length > 0 && (
                  <span className="absolute right-3 top-1/2 -translate-y-1/2">
                    {matchValid ? (
                      <Check size={16} color="#3F8F5F" />
                    ) : (
                      <span className="block w-1.5 h-1.5 rounded-full" style={{ background: "#C9683F" }} />
                    )}
                  </span>
                )}
              </div>
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
              disabled={!canSubmit}
              onClick={handleSubmit}
              className="w-full py-3 rounded-lg text-[15px] font-medium transition-all duration-200"
              style={{
                fontFamily: "Inter, sans-serif",
                background: canSubmit ? "#C9683F" : "#E5DAC8",
                color: canSubmit ? "#FBF6EF" : "#A99C8C",
                cursor: canSubmit ? "pointer" : "not-allowed",
              }}
            >
              {submitting ? "Updating..." : "Update password"}
            </button>
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