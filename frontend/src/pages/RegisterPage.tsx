import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getErrorMessage } from '../utils/getErrorMessage';

function IconCheck() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

const STEPS = [
  {
    title: 'Create your account',
    desc: 'Just a few details to get you started.',
  },
  {
    title: 'Meet your AI travel twin',
    desc: 'It learns your style, pace, and budget.',
  },
  {
    title: 'Get a personalized itinerary',
    desc: 'Routes, stays, and stops — planned for you.',
  },
  {
    title: 'Start exploring',
    desc: 'Every journey tells a story. Yours starts now.',
  },
];

export function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      await register({ name, email, password });
      navigate('/dashboard');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="min-h-screen bg-charcoal font-display flex items-center justify-center p-6">
      <div className="w-full max-w-4xl grid md:grid-cols-[1fr_1.1fr] rounded-2xl overflow-hidden border border-terracotta/20">

        {/* Left: journey stepper panel */}
        <div className="hidden md:flex flex-col justify-center bg-terracotta/5 p-10 relative">
          <p className="text-2xl font-bold text-cream mb-1">Voyage<span className="text-terracotta">AI</span></p>
          <p className="text-cream/50 text-sm mb-10">Your AI Travel Companion</p>

          <div className="relative">
            {STEPS.map((step, i) => (
              <div key={step.title} className="flex gap-4 relative">
                <div className="flex flex-col items-center">
                  <div className="w-7 h-7 rounded-full border-2 border-terracotta flex items-center justify-center text-terracotta shrink-0 bg-charcoal z-10">
                    <IconCheck />
                  </div>
                  {i < STEPS.length - 1 && (
                    <div className="w-px flex-1 min-h-[36px] bg-terracotta/30" />
                  )}
                </div>
                <div className="pb-8">
                  <p className="text-cream font-semibold text-sm">{step.title}</p>
                  <p className="text-cream/50 text-xs font-sans mt-0.5">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: form */}
        <div className="bg-charcoal p-10">
          <h2 className="text-3xl font-bold text-cream mb-1">Create account</h2>
          <p className="text-cream/50 text-sm mb-8">Begin planning your next adventure</p>

          <form onSubmit={handleSubmit}>
            {error && <p className="text-terracotta text-sm mb-4 font-medium">{error}</p>}

            <label className="block text-cream/70 text-sm font-medium mb-1">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full bg-cream/5 text-cream rounded-lg px-3 py-2.5 mb-4 outline-none border border-cream/15 focus:border-terracotta transition font-sans"
            />

            <label className="block text-cream/70 text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-cream/5 text-cream rounded-lg px-3 py-2.5 mb-4 outline-none border border-cream/15 focus:border-terracotta transition font-sans"
            />

            <div className="grid grid-cols-2 gap-3 mb-6">
              <div>
                <label className="block text-cream/70 text-sm font-medium mb-1">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full bg-cream/5 text-cream rounded-lg px-3 py-2.5 outline-none border border-cream/15 focus:border-terracotta transition font-sans"
                />
              </div>
              <div>
                <label className="block text-cream/70 text-sm font-medium mb-1">Confirm</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="w-full bg-cream/5 text-cream rounded-lg px-3 py-2.5 outline-none border border-cream/15 focus:border-terracotta transition font-sans"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-terracotta hover:bg-terracotta/90 text-cream font-semibold rounded-lg py-3 transition"
            >
              Begin Journey
            </button>

            <p className="text-cream/50 text-sm mt-6 text-center font-sans">
              Already have an account? <Link to="/login" className="text-terracotta font-semibold hover:underline">Log in</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}