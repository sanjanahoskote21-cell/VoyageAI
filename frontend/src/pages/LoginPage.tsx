import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getErrorMessage } from "../utils/getErrorMessage";

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
    console.error('Login failed:', err);
    setError(getErrorMessage(err, 'Invalid email or password.'));
}

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <form onSubmit={handleSubmit} className="bg-slate-800 rounded-lg p-8 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-white mb-6">Log in to VoyageAI</h1>

        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        <label className="block text-slate-400 text-sm mb-1">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 mb-4 outline-none focus:ring-2 focus:ring-purple-500"
        />

        <label className="block text-slate-400 text-sm mb-1">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 mb-6 outline-none focus:ring-2 focus:ring-purple-500"
        />

        <button
          type="submit"
          className="w-full bg-purple-600 hover:bg-purple-700 text-white rounded-lg py-2 font-medium"
        >
          Log In
        </button>

        <p className="text-slate-400 text-sm mt-4 text-center">
          No account? <Link to="/register" className="text-purple-400 hover:underline">Register</Link>
        </p>
      </form>
    </div>
  );
}
}