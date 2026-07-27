import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Check, X, MapPin, ArrowLeft } from "lucide-react";
import { verifyEmail, resendVerification } from "../api/authApi";
import { getErrorMessage } from "../utils/getErrorMessage";

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [status, setStatus] = useState<"verifying" | "success" | "error">("verifying");
  const [error, setError] = useState("");
  const [resendEmail, setResendEmail] = useState("");
  const [resendSent, setResendSent] = useState(false);
  const [resending, setResending] = useState(false);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setError("This verification link is missing its token.");
      return;
    }
    verifyEmail(token)
      .then(() => setStatus("success"))
      .catch((err) => {
        setStatus("error");
        setError(getErrorMessage(err));
      });
  }, [token]);

  const handleResend = async () => {
    if (!resendEmail.trim() || resending) return;
    setResending(true);
    try {
      await resendVerification(resendEmail);
      setResendSent(true);
    } finally {
      setResending(false);
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

        {status === "verifying" && (
          <p
            className="text-sm mt-4"
            style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
          >
            Verifying your email...
          </p>
        )}

        {status === "success" && (
          <>
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center mb-5 mt-2"
              style={{ background: "#EFE6D8" }}
            >
              <Check size={20} color="#3F8F5F" />
            </div>
            <h1
              className="text-[26px] leading-tight mb-2"
              style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#241E1A" }}
            >
              Email verified
            </h1>
            <p
              className="text-sm mb-6"
              style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
            >
              Your account is active. You can log in now.
            </p>
            <Link
              to="/login"
              className="inline-block px-5 py-2.5 rounded-lg text-[15px] font-medium"
              style={{
                background: "#C9683F",
                color: "#FBF6EF",
                fontFamily: "Inter, sans-serif",
                textDecoration: "none",
              }}
            >
              Go to log in
            </Link>
          </>
        )}

        {status === "error" && (
          <>
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center mb-5 mt-2"
              style={{ background: "#F4DCC8" }}
            >
              <X size={20} color="#C9683F" />
            </div>
            <h1
              className="text-[26px] leading-tight mb-2"
              style={{ fontFamily: "Fraunces, serif", fontWeight: 500, color: "#241E1A" }}
            >
              Link invalid or expired
            </h1>
            <p
              className="text-sm mb-5"
              style={{ color: "#8B7A66", fontFamily: "Inter, sans-serif" }}
            >
              {error || "This verification link no longer works."} Enter your email
              below to get a new one.
            </p>

            {!resendSent ? (
              <div className="flex gap-2">
                <input
                  type="email"
                  value={resendEmail}
                  onChange={(e) => setResendEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="flex-1 px-3.5 py-2.5 rounded-lg text-[15px] outline-none focus:ring-2"
                  style={{
                    fontFamily: "Inter, sans-serif",
                    background: "#F4EEE4",
                    border: "1px solid #DDD0BE",
                    color: "#241E1A",
                  }}
                />
                <button
                  onClick={handleResend}
                  disabled={resending}
                  className="px-4 py-2.5 rounded-lg text-sm font-medium"
                  style={{
                    background: "#C9683F",
                    color: "#FBF6EF",
                    fontFamily: "Inter, sans-serif",
                    opacity: resending ? 0.6 : 1,
                  }}
                >
                  {resending ? "Sending..." : "Resend"}
                </button>
              </div>
            ) : (
              <p
                className="text-sm"
                style={{ color: "#3F8F5F", fontFamily: "Inter, sans-serif" }}
              >
                If that account needs verifying, a new link is on its way.
              </p>
            )}
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