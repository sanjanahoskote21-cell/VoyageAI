import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchPlaces, type PlaceResponse } from '../api/placeApi';
import { createTrip } from '../api/tripApi';

export function TripPlannerPage() {
  const navigate = useNavigate();

  const [startLocation, setStartLocation] = useState('');
  const [endLocation, setEndLocation] = useState('');
  const [numDays, setNumDays] = useState(3);
  const [numTravelers, setNumTravelers] = useState(1);
  const [budgetTier, setBudgetTier] = useState('mid');
  const [travelMode, setTravelMode] = useState('car');

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PlaceResponse[]>([]);
  const [selectedPlaces, setSelectedPlaces] = useState<PlaceResponse[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    const results = await searchPlaces(searchQuery);
    setSearchResults(results);
  };

  const addPlace = (place: PlaceResponse) => {
    if (!selectedPlaces.find((p) => p.id === place.id)) {
      setSelectedPlaces((prev) => [...prev, place]);
    }
  };

  const removePlace = (placeId: string) => {
    setSelectedPlaces((prev) => prev.filter((p) => p.id !== placeId));
  };

  const handleSubmit = async () => {
    if (selectedPlaces.length === 0) {
      setError('Add at least one place to your trip.');
      return;
    }
    setError('');
    setIsSubmitting(true);
    try {
      const trip = await createTrip({
        start_location: startLocation,
        end_location: endLocation || undefined,
        num_days: numDays,
        num_travelers: numTravelers,
        budget_tier: budgetTier,
        travel_mode: travelMode,
        places: selectedPlaces.map((p) => ({ place_id: p.id })),
      });
      navigate(`/trips/${trip.id}`);
    } catch {
      setError('Failed to create trip. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Plan a New Trip</h1>

        {error && <p className="text-red-400 mb-4">{error}</p>}

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-slate-400 text-sm mb-1">Start Location</label>
            <input
              value={startLocation}
              onChange={(e) => setStartLocation(e.target.value)}
              className="w-full bg-slate-800 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-slate-400 text-sm mb-1">End Location (optional)</label>
            <input
              value={endLocation}
              onChange={(e) => setEndLocation(e.target.value)}
              className="w-full bg-slate-800 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-slate-400 text-sm mb-1">Number of Days</label>
            <input
              type="number"
              min={1}
              value={numDays}
              onChange={(e) => setNumDays(Number(e.target.value))}
              className="w-full bg-slate-800 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-slate-400 text-sm mb-1">Travelers</label>
            <input
              type="number"
              min={1}
              value={numTravelers}
              onChange={(e) => setNumTravelers(Number(e.target.value))}
              className="w-full bg-slate-800 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-slate-400 text-sm mb-1">Budget Tier</label>
            <select
              value={budgetTier}
              onChange={(e) => setBudgetTier(e.target.value)}
              className="w-full bg-slate-800 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="budget">Budget</option>
              <option value="mid">Mid</option>
              <option value="luxury">Luxury</option>
            </select>
          </div>
          <div>
            <label className="block text-slate-400 text-sm mb-1">Travel Mode</label>
            <select
              value={travelMode}
              onChange={(e) => setTravelMode(e.target.value)}
              className="w-full bg-slate-800 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="car">Car</option>
              <option value="bike">Bike</option>
              <option value="public_transport">Public Transport</option>
            </select>
          </div>
        </div>

        <h2 className="text-xl font-semibold mb-2">Add Places</h2>
        <div className="flex gap-2 mb-3">
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search places (e.g. Coorg, Mysore Palace)"
            className="flex-1 bg-slate-800 rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={handleSearch}
            className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg font-medium"
          >
            Search
          </button>
        </div>

        {searchResults.length > 0 && (
          <div className="grid gap-2 mb-4">
            {searchResults.map((place) => (
              <div key={place.id} className="flex justify-between items-center bg-slate-800 rounded-lg p-3">
                <div>
                  <p className="font-medium">{place.name}</p>
                  <p className="text-slate-400 text-sm">{place.city} · {place.category}</p>
                </div>
                <button
                  onClick={() => addPlace(place)}
                  className="bg-purple-600 hover:bg-purple-700 px-3 py-1 rounded-lg text-sm"
                >
                  Add
                </button>
              </div>
            ))}
          </div>
        )}

        {selectedPlaces.length > 0 && (
          <>
            <h2 className="text-xl font-semibold mb-2">Selected Places</h2>
            <div className="grid gap-2 mb-6">
              {selectedPlaces.map((place) => (
                <div key={place.id} className="flex justify-between items-center bg-slate-800 rounded-lg p-3">
                  <p>{place.name} ({place.city})</p>
                  <button
                    onClick={() => removePlace(place.id)}
                    className="text-red-400 hover:text-red-300 text-sm"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </>
        )}

        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-lg py-3 font-medium"
        >
          {isSubmitting ? 'Creating Trip...' : 'Create Trip'}
        </button>
      </div>
    </div>
  );
}