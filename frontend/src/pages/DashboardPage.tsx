import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listMyTrips } from '../api/tripApi';
import { useAuth } from '../hooks/useAuth';

export function DashboardPage() {
  const { user, logout } = useAuth();
  const { data: trips, isLoading, error } = useQuery({
    queryKey: ['trips'],
    queryFn: listMyTrips,
  });

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Hi, {user?.full_name}</h1>
          <div className="flex gap-4">
            <Link
              to="/trips/new"
              className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-medium"
            >
              + New Trip
            </Link>
            <button
              onClick={logout}
              className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg font-medium"
            >
              Logout
            </button>
          </div>
        </div>

        {isLoading && <p className="text-slate-400">Loading trips...</p>}
        {error && <p className="text-red-400">Failed to load trips.</p>}

        {trips && trips.length === 0 && (
          <p className="text-slate-400">No trips yet — create your first one!</p>
        )}

        <div className="grid gap-4">
          {trips?.map((trip) => (
            <Link
              key={trip.id}
              to={`/trips/${trip.id}`}
              className="block bg-slate-800 hover:bg-slate-700 rounded-lg p-4 transition"
            >
              <h2 className="text-xl font-semibold">
                {trip.start_location} → {trip.end_location || 'Multi-stop trip'}
              </h2>
              <p className="text-slate-400 text-sm">
                {trip.num_days} days · {trip.num_travelers} traveler(s) · {trip.budget_tier}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}