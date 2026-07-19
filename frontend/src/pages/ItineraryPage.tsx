import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getTrip } from '../api/tripApi';

export function ItineraryPage() {
  const { tripId } = useParams<{ tripId: string }>();
  const { data: trip, isLoading, error } = useQuery({
    queryKey: ['trip', tripId],
    queryFn: () => getTrip(tripId!),
    enabled: !!tripId,
  });

  if (isLoading) return <div className="min-h-screen bg-slate-900 text-white p-8">Loading...</div>;
  if (error || !trip) return <div className="min-h-screen bg-slate-900 text-white p-8">Failed to load trip.</div>;

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-3xl mx-auto">
        <Link to="/dashboard" className="text-purple-400 hover:underline text-sm">← Back to trips</Link>

        <h1 className="text-3xl font-bold mt-4 mb-2">
          {trip.start_location} → {trip.end_location || 'Multi-stop trip'}
        </h1>
        <p className="text-slate-400 mb-8">
          {trip.num_days} days · {trip.num_travelers} traveler(s) · {trip.budget_tier} · {trip.travel_mode}
        </p>

        {trip.total_distance_km != null && (
          <p className="text-slate-400 mb-6">
            Total distance: {trip.total_distance_km} km
            {trip.distance_saved_km ? ` (saved ${trip.distance_saved_km} km via route optimization)` : ''}
          </p>
        )}

        <h2 className="text-xl font-semibold mb-3">Places</h2>
        <div className="grid gap-3 mb-8">
          {trip.places
            .slice()
            .sort((a, b) => (a.visit_order ?? 0) - (b.visit_order ?? 0))
            .map((place) => (
              <div key={place.id} className="bg-slate-800 rounded-lg p-4">
                <p className="font-medium">{place.display_name}</p>
                {place.display_city && <p className="text-slate-400 text-sm">{place.display_city}</p>}
              </div>
            ))}
        </div>

        {trip.budget && (
          <>
            <h2 className="text-xl font-semibold mb-3">Budget</h2>
            <div className="bg-slate-800 rounded-lg p-4 grid grid-cols-2 gap-2 mb-8">
              <p className="text-slate-400">Hotel</p><p>₹{trip.budget.hotel_cost}</p>
              <p className="text-slate-400">Food</p><p>₹{trip.budget.food_cost}</p>
              <p className="text-slate-400">Fuel</p><p>₹{trip.budget.fuel_cost}</p>
              <p className="text-slate-400">Misc</p><p>₹{trip.budget.misc_cost}</p>
              <p className="font-semibold">Total</p><p className="font-semibold">₹{trip.budget.total_cost}</p>
            </div>
          </>
        )}

        <Link
          to={`/trips/${trip.id}/chat`}
          className="inline-block bg-purple-600 hover:bg-purple-700 px-5 py-3 rounded-lg font-medium"
        >
          Chat with Travel Twin →
        </Link>
      </div>
    </div>
  );
}