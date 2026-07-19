import axiosClient from './axiosClient';

export interface TripPlaceInput {
  place_id?: string;
  custom_name?: string;
  custom_city?: string;
}

export interface TripCreatePayload {
  start_location: string;
  end_location?: string;
  num_days: number;
  num_travelers: number;
  budget_tier: string;
  travel_mode: string;
  places: TripPlaceInput[];
}

export interface TripPlaceResponse {
  id: string;
  display_name: string;
  display_city?: string;
  resolved_latitude: number;
  resolved_longitude: number;
  visit_order?: number;
}

export interface BudgetEstimateResponse {
  hotel_cost: number;
  food_cost: number;
  fuel_cost: number;
  misc_cost: number;
  total_cost: number;
}

export interface TripResponse {
  id: string;
  start_location: string;
  end_location?: string;
  num_days: number;
  num_travelers: number;
  budget_tier: string;
  travel_mode: string;
  total_distance_km?: number;
  distance_saved_km?: number;
  created_at: string;
  places: TripPlaceResponse[];
  budget?: BudgetEstimateResponse;
}

export const createTrip = async (data: TripCreatePayload): Promise<TripResponse> => {
  const response = await axiosClient.post<TripResponse>('/trips/', data);
  return response.data;
};

export const getTrip = async (tripId: string): Promise<TripResponse> => {
  const response = await axiosClient.get<TripResponse>(`/trips/${tripId}`);
  return response.data;
};

export const listMyTrips = async (): Promise<TripResponse[]> => {
  const response = await axiosClient.get<TripResponse[]>('/trips/');
  return response.data;
};
