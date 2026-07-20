import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getErrorMessage } from '../utils/getErrorMessage';

function IconRoute() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="6" cy="19" r="3" /><circle cx="18" cy="5" r="3" />
      <path d="M9 19h7a4 4 0 0 0 4-4v-1a4 4 0 0 0-4-4H8a4 4 0 0 1-4-4v-1" />
    </svg>
  );
}
function IconCalendar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <path d="M16 2v4M8 2v4M3 10h18" />
    </svg>
  );
}
function IconWallet() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M21 12V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-1" />
      <path d="M18 12a2 2 0 0 0 0 4h3v-4Z" />
    </svg>
  );
}
function IconBot() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <rect x="3" y="8" width="18" height="12" rx="2" />
      <path d="M12 8V4M9 4h6" /><circle cx="8.5" cy="14" r="1.5" /><circle cx="15.5" cy="14" r="1.5" />
    </svg>
  );
}

function IconCompass() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
      <circle cx="12" cy="12" r="9" />
      <path d="M14.5 9.5 12 12l2.5 2.5L17 9.5l-2.5 2.5z" />
      <path d="M9.5 14.5 12 12 9.5 9.5 7 14.5l2.5 0z" />
    </svg>
  );
}
function IconMountain() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 20 9 8l4 7 2-3 6 8H3z" />
    </svg>
  );
}
function IconPlane() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12l20-8-8 20-2-9-9-3z" />
    </svg>
  );
}
function IconPalm() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22v-9M12 13c-2-3-6-3-9-1 2 2 5 2 9 1zM12 13c2-3 6-3 9-1-2 2-5 2-9 1zM12 13c-1-3 0-6 2-8-3 0-5 3-2 8z" />
    </svg>
  );
}

const FEATURES = [
  { Icon: IconRoute, label: 'Smart Route Optimization' },
  { Icon: IconCalendar, label: 'Personalized Itineraries' },
  { Icon: IconWallet, label: 'Budget Planner' },
  { Icon: IconBot, label: 'Your AI Travel Twin' },
];

const STAMPS = [
  { Icon: IconCompass, rotate: -6 },
  { Icon: IconPlane, rotate: 4 },
  { Icon: IconMountain, rotate: -3 },
  { Icon: IconPalm, rotate: 7 },
];

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login({ email, password });
      navigate('/dashboard');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="min-h-screen bg-charcoal font-display flex items-center p-6">
      <style>{`
        @keyframes stampFloat {
          0%, 100% { transform: translateY(0) rotate(var(--r, 0deg)); }
          50% { transform: translateY(-6px) rotate(var(--r, 0deg)); }
        }
      `}</style>

      <div className="w-full max-w-6xl mx-0 md:ml-16 grid md:grid-cols-[1fr_auto_auto] gap-10 items-center">

        <div className="text-left max-w-md">
          <p className="text-2xl font-bold text-cream mb-1">Voyage<span className="text-terracotta">AI</span></p>
          <p className="text-cream/50 text-sm mb-8">Your AI Travel Companion</p>

          <h1 className="text-5xl font-bold text-cream leading-tight mb-4">
            Every journey<br />
            <span className="italic text-terracotta">tells a story.</span>
          </h1>
          <p className="text-cream/60 mb-10">Plan smarter. Travel better. Let AI be your guide.</p>

          <div className="space-y-4">
            {FEATURES.map(({ Icon, label }) => (
              <div key={label} className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg border border-terracotta/40 flex items-center justify-center shrink-0 text-terracotta">
                  <Icon />
                </div>
                <span className="text-cream/80 font-sans text-sm">{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Passport stamp divider — decorative, travel-themed, no fabricated data */}
        <div className="hidden md:flex flex-col items-center justify-center h-[420px] gap-8 relative">
          <div className="absolute top-0 bottom-0 w-px border-l border-dashed border-terracotta/25" />
          {STAMPS.map(({ Icon, rotate }, i) => (
            <div
              key={i}
              className="relative w-14 h-14 rounded-full border-2 border-terracotta/50 flex items-center justify-center text-terracotta bg-charcoal"
              style={{
                ['--r' as string]: `${rotate}deg`,
                transform: `rotate(${rotate}deg)`,
                animation: 'stampFloat 4s ease-in-out infinite',
                animationDelay: `${i * 0.4}s`,
              }}
            >
              <div className="absolute inset-[3px] rounded-full border border-terracotta/25" />
              <Icon />
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="bg-charcoal border border-terracotta/20 rounded-2xl p-8 w-full max-w-sm">
          <h2 className="text-3xl font-bold text-cream mb-1">Welcome back</h2>
          <p className="text-cream/50 text-sm mb-8">Log in to continue your journey</p>

          {error && <p className="text-terracotta text-sm mb-4 font-medium">{error}</p>}

          <label className="block text-cream/70 text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full bg-cream/5 text-cream rounded-lg px-3 py-2.5 mb-4 outline-none border border-cream/15 focus:border-terracotta transition font-sans"
          />

          <label className="block text-cream/70 text-sm font-medium mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full bg-cream/5 text-cream rounded-lg px-3 py-2.5 mb-6 outline-none border border-cream/15 focus:border-terracotta transition font-sans"
          />

          <button
            type="submit"
            className="w-full bg-terracotta hover:bg-terracotta/90 text-cream font-semibold rounded-lg py-3 transition"
          >
            Continue Journey
          </button>

          <p className="text-cream/50 text-sm mt-6 text-center font-sans">
            No account? <Link to="/register" className="text-terracotta font-semibold hover:underline">Register</Link>
          </p>
        </form>
      </div>
    </div>
  );
}